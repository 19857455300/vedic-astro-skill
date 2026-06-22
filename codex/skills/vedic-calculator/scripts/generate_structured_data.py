#!/usr/bin/env python3
"""Generate a canonical structured_data.md from birth information."""

import argparse
from contextlib import redirect_stdout
from datetime import datetime
import io
from pathlib import Path
import re
import sys

import pytz


SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


def parse_date(value):
    """Parse an ISO date and reject non-YYYY-MM-DD input."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise argparse.ArgumentTypeError(
            f"invalid date '{value}': expected YYYY-MM-DD"
        )
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"invalid date '{value}': {exc}"
        ) from exc


def parse_time(value):
    """Parse a 24-hour time and reject non-HH:MM input."""
    if not re.fullmatch(r"\d{2}:\d{2}", value):
        raise argparse.ArgumentTypeError(
            f"invalid time '{value}': expected HH:MM in 24-hour format"
        )
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"invalid time '{value}': expected a valid HH:MM in 24-hour format"
        ) from exc


def latitude(value):
    return bounded_float(value, "lat", -90.0, 90.0)


def longitude(value):
    return bounded_float(value, "lon", -180.0, 180.0)


def bounded_float(value, name, minimum, maximum):
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"invalid {name} '{value}': expected a number"
        ) from exc
    if not minimum <= number <= maximum:
        raise argparse.ArgumentTypeError(
            f"invalid {name} '{value}': expected {minimum:g} to {maximum:g}"
        )
    return number


def timezone_name(value):
    try:
        pytz.timezone(value)
    except pytz.UnknownTimeZoneError as exc:
        raise argparse.ArgumentTypeError(
            f"invalid timezone '{value}': expected an IANA timezone such as Asia/Shanghai"
        ) from exc
    return value


def build_parser():
    parser = argparse.ArgumentParser(
        description="Generate vedic-calculator structured_data.md"
    )
    parser.add_argument("--date", required=True, type=parse_date, help="YYYY-MM-DD")
    parser.add_argument("--time", required=True, type=parse_time, help="HH:MM")
    parser.add_argument("--place", required=True, help="Birth place text")
    parser.add_argument("--lat", required=True, type=latitude, help="Latitude")
    parser.add_argument("--lon", required=True, type=longitude, help="Longitude")
    parser.add_argument(
        "--tz",
        required=True,
        type=timezone_name,
        help="IANA timezone, for example Asia/Shanghai",
    )
    parser.add_argument(
        "--output",
        default="structured_data.md",
        help="Output file path (default: structured_data.md)",
    )
    parser.add_argument("--gender", default="未提供")
    parser.add_argument("--relationship", default="未提供")
    parser.add_argument("--time-precision", default="精确到分钟")
    parser.add_argument("--time-source", default="用户提供")
    return parser


def main():
    args = build_parser().parse_args()
    birth_date = args.date
    birth_time = args.time

    try:
        with redirect_stdout(io.StringIO()):
            from engine import calculate_full_chart
            from formatter import format_structured_data
            from transit import calc_transit

            chart = calculate_full_chart(
                year=birth_date.year,
                month=birth_date.month,
                day=birth_date.day,
                hour=birth_time.hour,
                minute=birth_time.minute,
                lat=args.lat,
                lon=args.lon,
                tz_str=args.tz,
            )
            transit = calc_transit(
                chart["lagna"]["sign_idx"],
                chart["planets"]["Moon"]["sign_idx"],
                args.tz,
            )

        sav_total = sum(chart["sav"].get(sign, 0) for sign in SIGNS)
        if sav_total != 337:
            print(
                f"ERROR: SAV validation failed: expected 337, got {sav_total}",
                file=sys.stderr,
            )
            return 1

        meta = {
            "dob": birth_date.strftime("%Y-%m-%d"),
            "time": birth_time.strftime("%H:%M"),
            "place": args.place,
            "lat": args.lat,
            "lon": args.lon,
            "time_precision": args.time_precision,
            "time_source": args.time_source,
        }
        user_info = {
            "gender": args.gender,
            "relationship": args.relationship,
        }
        markdown = format_structured_data(chart, transit, meta, user_info)

        output_path = Path(args.output).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    except Exception as exc:
        print(f"ERROR: failed to generate structured_data.md: {exc}", file=sys.stderr)
        return 1

    print(f"Output file: {output_path}")
    print(f"SAV total: {sav_total}")
    print(f"Lagna: {chart['lagna']['sign']}")
    print(f"Moon sign: {chart['planets']['Moon']['sign']}")
    print("structured_data.md generated successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
