import argparse
import asyncio
import os
import sys

from builder import MarksheetBuilder

async def main(arglist):
    parser = argparse.ArgumentParser(description='Downloads student marksheets from https://resultsarchives.nic.in/cbseresults/cbseresults2011/class1211/cbse1211.htm')
    parser.add_argument('--filename', dest='filename', required=True)
    parser.add_argument('--start-roll', dest='start_roll', required=True)
    parser.add_argument('--end-roll', dest='end_roll', required=True)
    args = parser.parse_args(arglist[1:])

    builder = MarksheetBuilder()
    await builder.download_student_marks(int(args.start_roll), int(args.end_roll))
    CUR_DIR = os.path.dirname(__file__)
    csv_filepath = os.path.join(CUR_DIR, args.filename)
    builder.create_csv(csv_filepath)

asyncio.run(main(sys.argv))
