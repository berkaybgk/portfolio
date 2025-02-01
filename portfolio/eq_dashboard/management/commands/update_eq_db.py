from django.core.management.base import BaseCommand
from ...eq_data_utils import EqUtils
from ...cron import update_latest_eq_data
import os


class Command(BaseCommand):
    help = 'Update the earthquake database'

    def add_arguments(self, parser):
        parser.add_argument('lookback_days', type=int, help='Number of days to look back for earthquake data')

    def handle(self, *args, **kwargs):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        data_path = "../../resources/eq_data.csv"

        lookback_days = kwargs['lookback_days']

        update_latest_eq_data(lookback_days)

        data_path = os.path.join(current_dir, data_path)

        eq_utils = EqUtils()
        eq_utils.read_csv_into_db_usgs(data_path)

        self.stdout.write(self.style.SUCCESS('Successfully updated the earthquake database'))





