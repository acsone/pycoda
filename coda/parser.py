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
#

import time
from statement import Statement
from coda.statement import MovementRecord, MovementRecordType, InformationRecord,\
    FreeCommunication


class CodaParserException(Exception):

    """Exception raised for errors in the input.

    Attributes:
        code -- exception code
        msg  -- explanation of the error
    """

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg


class Parser(object):

    """CODA file parser mapping line to Python objects
    """

    def __init__(self, date_format='%Y-%m-%d'):
        self.date_format = date_format

    def parse(self, value):
        recordlist = unicode(value, 'windows-1252', 'strict').split('\n')
        statements = []
        statement = None
        for line in recordlist:
            if not line:
                pass
            elif line[0] == '0':
                self.__fixes_globalisation_without_details(
                    statement)
                # Begin of a new Bank statement
                statement = Statement()
                self._parseHeader(line, statement)
                statements.append(statement)

            elif line[0] == '1':
                # Statement details
                self._parseHeaderDetails(line, statement)
            elif line[0] == '2':
                self._parseMovementRecord(line, statement)
            elif line[0] == '3':
                self._parseInformationRecord(line, statement)
            elif line[0] == '4':
                self.parseFreeCommunication(line, statement)
            elif line[0] == '8':
                # new balance record
                self._parseNewBalanceRecord(line, statement)
            elif line[0] == '9':
                # trailer record
                pass
        self.__fixes_globalisation_without_details(statement)
        return statements

    def __fixes_globalisation_without_details(self, statement):
        """ Change the movement type from globalisation to normal for the last
        movements
        """
        if statement and statement.movements:
            mv = statement.movements[-1]
            if mv.type == MovementRecordType.GLOBALISATION:
                mv.type = MovementRecordType.NORMAL

    def _parseHeader(self, line, statement):
        statement.version = version = line[127]
        if version not in ['1', '2']:
            raise CodaParserException(
                ' R001', 'CODA V%s statements are not supported, please contact your bank' % statement.version)
        statement.creation_date = time.strftime(
            self.date_format, time.strptime(rmspaces(line[5:11]), '%d%m%y'))
        statement.separate_application = rmspaces(line[83:88])

    def _parseHeaderDetails(self, line, statement):
        if statement.version == '1':
            statement.acc_number = rmspaces(line[5:17])
            statement.currency = rmspaces(line[18:21])
        elif statement.version == '2':
            if line[1] == '0':  # Belgian bank account BBAN structure
                statement.acc_number = rmspaces(line[5:17])
                statement.currency = rmspaces(line[18:21])
            elif line[1] == '1':  # foreign bank account BBAN structure
                raise CodaParserException(
                    ' R1001', 'Foreign bank accounts with BBAN structure are not supported ')
            elif line[1] == '2':  # Belgian bank account IBAN structure
                statement.acc_number = rmspaces(line[5:21])
                statement.currency = rmspaces(line[39:42])
            elif line[1] == '3':  # foreign bank account IBAN structure
                raise CodaParserException(
                    ' R1002', 'Foreign bank accounts with IBAN structure are not supported ')
            else:  # Something else, not supported
                raise CodaParserException(
                    ' R1003', 'Unsupported bank account structure ')

        statement.description = rmspaces(line[90:125])
        statement.old_balance = float(rmspaces(line[43:58])) / 1000
        statement.old_balance_amount_sign = line[42]
        statement.old_balance_date = time.strftime(
            self.date_format, time.strptime(rmspaces(line[58:64]), '%d%m%y'))
        statement.account_holder_name = rmspaces(line[64:90])
        statement.paper_seq_number = rmspaces(line[2:5])
        statement.coda_seq_number = rmspaces(line[125:128])

    def _parseMovementRecord(self, line, statement):
        if line[1] == '1':
            # New statement line
            record = MovementRecord()
            record.ref = rmspaces(line[2:10])
            record.ref_move = rmspaces(line[2:6])
            record.ref_move_detail = rmspaces(line[6:10])
            record.transaction_ref = rmspaces(line[10:31])
            record.transaction_amount_sign = line[31]  # 0 = Credit, 1 = Debit
            record.transaction_amount = float(rmspaces(line[32:47])) / 1000
            record.transaction_type = int(line[53])
            record.transaction_date = time.strftime(
                self.date_format, time.strptime(rmspaces(line[47:53]), '%d%m%y'))
            record.transaction_family = rmspaces(line[54:56])
            record.transaction_code = rmspaces(line[56:58])
            record.transaction_category = rmspaces(line[58:61])
            record.communication_is_structured = line[61] == '1'
            if record.communication_is_structured:
                # Structured communication
                record.communication_type = line[62:65]
                record.communication = '+++' + \
                    line[65:68] + '/' + line[68:72] + '/' + line[72:77] + '+++'
            else:
                # Non-structured communication
                record.communication = rmspaces(line[62:115])
            record.entry_date = time.strftime(
                self.date_format, time.strptime(rmspaces(line[115:121]), '%d%m%y'))
            record.type = MovementRecordType.NORMAL

            if record.transaction_type in [1, 2, 3]:
                # here the transaction type is a globalisation
                # 1 is for globalisation from the customer
                # 2 is for globalisation from the bank
                record.type = MovementRecordType.GLOBALISATION

            # a globalisation record can be followed by details lines
            # if it's not the case, the globalisation record is considered
            # as normal. To determine if a globalisation record is followed
            # by details, on a new line starting with 21, we check if the
            # previous line is a globalisation record. If the current line is
            # not a details line (transaction_type > 3) we reset the
            # record.type to Normal
            prev_mvmt = statement.movements and statement.movements[-1] or None
            if prev_mvmt and \
                record.transaction_type < 4 and \
                    prev_mvmt.type == MovementRecordType.GLOBALISATION:
                prev_mvmt.type = MovementRecordType.NORMAL
            record.globalisation_code = int(line[124])
            statement.movements.append(record)
        elif line[1] == '2':
            record = statement.movements[-1]
            if record.ref[0:4] != line[2:6]:
                raise CodaParserException(
                    'R2004', 'CODA parsing error on movement data record 2.2, '
                    'seq nr %s!' % line[2:10])
            record.communication = join_communications(
                record.communication, rmspaces(line[10:63]))
            record.payment_reference = rmspaces(line[63:98])
            record.counterparty_bic = rmspaces(line[98:109])
        elif line[1] == '3':
            record = statement.movements[-1]
            if record.ref[0:4] != line[2:6]:
                raise CodaParserException(
                    'R2005', 'CODA parsing error on movement data record 2.3, '
                    'eq nr %s!' % line[2:10])
            if statement.version == '1':
                record.counterparty_number = rmspaces(line[10:22])
                record.counterparty_name = rmspaces(line[47:73])
                record.counterparty_address = rmspaces(line[73:125])
                record.counterparty_currency = ''
            else:
                if line[22] == ' ':
                    record.counterparty_number = rmspaces(line[10:22])
                    record.counterparty_currency = rmspaces(line[23:26])
                else:
                    record.counterparty_number = rmspaces(line[10:44])
                    record.counterparty_currency = rmspaces(line[44:47])
                record.counterparty_name = rmspaces(line[47:82])
                record.communication = join_communications(
                    record.communication, rmspaces(line[82:125]))
        else:
            # movement data record 2.x (x != 1,2,3)
            raise CodaParserException(
                'R2006', '\nMovement data records of type 2.%s are not supported ' % line[1])

    def _parseInformationRecord(self, line, statement):
        if line[1] == '1':
            infoLine = InformationRecord()
            infoLine.ref = rmspaces(line[2:10])
            infoLine.transaction_ref = rmspaces(line[10:31])
            infoLine.transaction_type = line[31]
            infoLine.transaction_family = rmspaces(line[32:34])
            infoLine.transaction_code = rmspaces(line[34:36])
            infoLine.transaction_category = rmspaces(line[36:39])
            infoLine.communication = rmspaces(line[40:113])
            statement.informations.append(infoLine)
        elif line[1] == '2':
            infoLine = statement.informations[-1]
            if infoLine.ref != rmspaces(line[2:10]):
                raise CodaParserException(
                    'R3004', 'CODA parsing error on information data '
                    'record 3.2, seq nr %s!' % line[2:10])
            infoLine.communication += rmspaces(line[10:100])
        elif line[1] == '3':
            infoLine = statement.informations[-1]
            if infoLine.ref != rmspaces(line[2:10]):
                raise CodaParserException(
                    'R3005', 'CODA parsing error on information data '
                    'record 3.3, seq nr %s!' % line[2:10])
            infoLine.communication += rmspaces(line[10:100])

    def _parseNewBalanceRecord(self, line, statement):
        statement.new_balance_amount_sign = line[41]
        statement.new_balance_paper_seq_number = rmspaces(line[1:4])
        statement.new_balance = float(rmspaces(line[42:57])) / 1000
        statement.new_balance_date = time.strftime(
            self.date_format, time.strptime(rmspaces(line[57:63]), '%d%m%y'))

    def parseFreeCommunication(self, line, statement):
        comm_line = FreeCommunication()
        comm_line.ref = rmspaces(line[2:10])
        comm_line.communication = rmspaces(line[32:112])
        statement.free_comunications.append(comm_line)


def join_communications(c1, c2):
    if not c1:
        return c2
    if not c2:
        return c1
    if not c2.startswith(" "):
        return " ".join([c1, c2])
    return c1 + c2


def rmspaces(s):
    return " ".join(s.split())

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
