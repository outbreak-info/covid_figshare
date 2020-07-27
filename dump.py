import os

import biothings, config
biothings.config_for_app(config)
from config import DATA_ARCHIVE_ROOT

import biothings.hub.dataload.dumper


class FigshareDumper(biothings.hub.dataload.dumper.DummyDumper):
    # type: resource
    SRC_NAME = "covid_figshare"
    # override in subclass accordingly
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    __metadata__ = {
        "src_meta": {
            'license_url': 'https://figshare.com/terms',
            'url': 'https://covid19.figshare.com/'
        }
    }

    SCHEDULE = "0 6 * * *"
