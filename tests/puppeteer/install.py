#!/usr/bin/env python

import sys
sys.path.append('../../scripts')
import base
import os

os.environ["PUPPETEER_SKIP_CHROMIUM_DOWNLOAD"] = "true"
base.cmd("npm", ["i", "puppeteer"])
