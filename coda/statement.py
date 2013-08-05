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
    ref = None

    # Continuous sequence number Starts at 0001 and is increased by 1 for
    # each movement record referring to
    # another movement on the daily statement
    # of account.
    ref_move = None

    # Detail number for
    # each movement record for the same
    # continuous sequence number.
    ref_move_detail = None
    transaction_ref = None
    transaction_amount = None
    transaction_amount_sign = None
    transaction_type = None
    transaction_date = None
    transaction_family = None
    transaction_code = None
    transaction_category = None
    communication_is_structured = None
    communication_type = None
    communication = None
    entry_date = None
    type = None
    globalisation_code = None
    payment_reference = None
    counterparty_bic = None
    counterparty_number = None
    counterparty_name = None
    counterparty_address = None
    counterparty_currency = None


class InformationRecord(object):

    """ Information record
    """
    ref = None
    transaction_ref = None
    transaction_type = None
    transaction_family = None
    transaction_code = None
    transaction_category = None
    communication = None


class FreeCommunication(object):

    """ Free communication
    """
    ref = None
    communication = None


class Statement(object):

    """Statement of account
    """

    creation_date = None
    separate_application = None
    version = None
    acc_number = None
    currency = None
    description = None
    old_balance = None
    old_balance_amount_sign = None
    old_balance_date = None
    account_holder_name = None
    paper_seq_number = None
    coda_seq_number = None
    new_balance = None
    new_balance_amount_sign = None
    new_balance_date = None
    new_balance_paper_seq_number = None
    movements = []
    informations = []
    free_comunications = []


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
