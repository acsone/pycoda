# -*- coding: utf-8 -*-
#
# Authors: Laurent Mignon
# Copyright (c) 2013 Acsone SA/NV (http://www.acsone.eu)
# All Rights Reserved
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contact a Free Software
# Service Company.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#


class AmountSign(object):
    CREDIT = "0"
    DEBIT = "1"


class MovementRecordType(object):
    NORMAL = "0"
    GLOBALISATION = "1"


class MovementRecord(object):
    """A movement record
    """

    def __init__(self):
        self.ref = None

        # Continuous sequence number Starts at 0001 and is increased by 1 for
        # each movement record referring to
        # another movement on the daily statement
        # of account.
        self.ref_move = None

        # Detail number for
        # each movement record for the same
        # continuous sequence number.
        self.ref_move_detail = None
        self.transaction_ref = None
        self.transaction_amount = None
        self.transaction_amount_sign = None
        self.transaction_type = None
        self.transaction_date = None
        self.transaction_family = None
        self.transaction_code = None
        self.transaction_category = None
        self.communication_is_structured = None
        self.communication_type = None
        self.communication = None
        self.entry_date = None
        self.type = None
        self.globalisation_code = None
        self.payment_reference = None
        self.counterparty_bic = None
        self.counterparty_number = None
        self.counterparty_name = None
        self.counterparty_address = None
        self.counterparty_currency = None


class InformationRecord(object):
    """ Information record
    """

    def __init__(self):
        self.ref = None
        # Continuous sequence number: must be identical to
        # the continuous sequence number of the movement
        # record to which the information record refers.
        self.ref_move = None
        # Detail number 
        self.ref_move_detail = None
        self.transaction_ref = None
        self.transaction_type = None
        self.transaction_family = None
        self.transaction_code = None
        self.transaction_category = None
        self.communication = None


class FreeCommunication(object):
    """ Free communication
    """
    def __init__(self):
        self.ref = None
        self.communication = None


class Statement(object):
    """Statement of account
    """

    def __init__(self):
        self.creation_date = None
        self.separate_application = None
        self.version = None
        self.acc_number = None
        self.currency = None
        self.description = None
        self.old_balance = None
        self.old_balance_amount_sign = None
        self.old_balance_date = None
        self.account_holder_name = None
        self.paper_seq_number = None
        self.coda_seq_number = None
        self.new_balance = None
        self.new_balance_amount_sign = None
        self.new_balance_date = None
        self.new_balance_paper_seq_number = None
        self.movements = []
        self.informations = []
        self.free_comunications = []
