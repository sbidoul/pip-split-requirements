# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@acsone.eu>
# SPDX-License-Identifier: MIT

import sys

__all__ = ["Protocol"]


if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol
