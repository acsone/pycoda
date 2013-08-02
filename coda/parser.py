# -*- coding: utf-8 -*-
##############################################################################
#
# Authors: Laurent Mignon & Stéphane Bidoul
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
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import base64
import time

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

    def parse(self, value, date_format='%Y-%m-%d'): 
        recordlist = unicode(value, 'windows-1252', 'strict').split('\n')
        statements = []
        for line in recordlist:
            if not line:
                pass
            elif line[0] == '0':
                #Begin of a new Bank statement
                statement = {}
                statements.append(statement)
                statement['version'] = line[127]
                if statement['version'] not in ['1', '2']:
                    raise CodaParserException(' R001', _('CODA V%s statements are not supported, please contact your bank') % statement['version'])
                statement['globalisation_stack'] = []
                statement['lines'] = []
                statement['date'] = time.strftime(date_format, time.strptime(rmspaces(line[5:11]), '%d%m%y'))
                statement['separateApplication'] = rmspaces(line[83:88])
            elif line[0] == '1':
                #Statement details
                if statement['version'] == '1':
                    statement['acc_number'] = rmspaces(line[5:17])
                    statement['currency'] = rmspaces(line[18:21])
                elif statement['version'] == '2':
                    if line[1] == '0':  # Belgian bank account BBAN structure
                        statement['acc_number'] = rmspaces(line[5:17])
                        statement['currency'] = rmspaces(line[18:21])
                    elif line[1] == '1':  # foreign bank account BBAN structure
                        raise CodaParserException(' R1001', _('Foreign bank accounts with BBAN structure are not supported '))
                    elif line[1] == '2':    # Belgian bank account IBAN structure
                        statement['acc_number'] = rmspaces(line[5:21])
                        statement['currency'] = rmspaces(line[39:42])
                    elif line[1] == '3':    # foreign bank account IBAN structure
                        raise CodaParserException(' R1002', _('Foreign bank accounts with IBAN structure are not supported '))
                    else:  # Something else, not supported
                        raise CodaParserException(' R1003', _('Unsupported bank account structure '))
                statement['journal_id'] = False
                statement['bank_account'] = False
                statement['description'] = rmspaces(line[90:125])
                statement['balance_start'] = float(rmspaces(line[43:58])) / 1000
                if line[42] == '1':    #1 = Debit, the starting balance is negative
                    statement['balance_start'] = - statement['balance_start']
                statement['balance_start_date'] = time.strftime(date_format, time.strptime(rmspaces(line[58:64]), '%d%m%y'))
                statement['accountHolder'] = rmspaces(line[64:90])
                statement['paperSeqNumber'] = rmspaces(line[2:5])
                statement['codaSeqNumber'] = rmspaces(line[125:128])
            elif line[0] == '2':
                if line[1] == '1':
                    #New statement line
                    statementLine = {}
                    statementLine['ref'] = rmspaces(line[2:10])
                    statementLine['ref_move'] = rmspaces(line[2:6])
                    statementLine['ref_move_detail'] = rmspaces(line[6:10])
                    statementLine['sequence'] = len(statement['lines']) + 1
                    statementLine['transactionRef'] = rmspaces(line[10:31])
                    statementLine['debit'] = line[31]  # 0 = Credit, 1 = Debit
                    statementLine['amount'] = float(rmspaces(line[32:47])) / 1000
                    if statementLine['debit'] == '1':
                        statementLine['amount'] = - statementLine['amount']
                    statementLine['transaction_type'] = line[53]
                    statementLine['transactionDate'] = time.strftime(date_format, time.strptime(rmspaces(line[47:53]), '%d%m%y'))
                    statementLine['transaction_family'] = rmspaces(line[54:56])
                    statementLine['transaction_code'] = rmspaces(line[56:58])
                    statementLine['transaction_category'] = rmspaces(line[58:61])
                    if line[61] == '1':
                        #Structured communication
                        statementLine['communication_struct'] = True
                        statementLine['communication_type'] = line[62:65]
                        statementLine['communication'] = '+++' + line[65:68] + '/' + line[68:72] + '/' + line[72:77] + '+++'
                    else:
                        #Non-structured communication
                        statementLine['communication_struct'] = False
                        statementLine['communication'] = rmspaces(line[62:115])
                    statementLine['entryDate'] = time.strftime(date_format, time.strptime(rmspaces(line[115:121]), '%d%m%y'))
                    statementLine['type'] = 'normal'
                    statementLine['globalisation'] = int(line[124])
                    if len(statement['globalisation_stack']) > 0 and statementLine['communication'] != '':
                        statementLine['communication'] = "\n".join([statement['globalisation_stack'][-1]['communication'], statementLine['communication']])
                    if statementLine['globalisation'] > 0:
                        if len(statement['globalisation_stack']) > 0 and statement['globalisation_stack'][-1]['globalisation'] == statementLine['globalisation']:
                            # Destack
                            statement['globalisation_stack'].pop()
                        else:
                            #Stack
                            statementLine['type'] = 'globalisation'
                            statement['globalisation_stack'].append(statementLine)
                    statement['lines'].append(statementLine)
                elif line[1] == '2':
                    if statement['lines'][-1]['ref'][0:4] != line[2:6]:
                        raise CodaParserException('R2004', _('CODA parsing error on movement data record 2.2, seq nr %s! Please report this issue via your OpenERP support channel.') % line[2:10])
                    statement['lines'][-1]['communication'] += rmspaces(line[10:63])
                    statement['lines'][-1]['payment_reference'] = rmspaces(line[63:98])
                    statement['lines'][-1]['counterparty_bic'] = rmspaces(line[98:109])
                elif line[1] == '3':
                    if statement['lines'][-1]['ref'][0:4] != line[2:6]:
                        raise CodaParserException('R2005', _('CODA parsing error on movement data record 2.3, seq nr %s! Please report this issue via your OpenERP support channel.') % line[2:10])
                    if statement['version'] == '1':
                        statement['lines'][-1]['counterpartyNumber'] = rmspaces(line[10:22])
                        statement['lines'][-1]['counterpartyName'] = rmspaces(line[47:73])
                        statement['lines'][-1]['counterpartyAddress'] = rmspaces(line[73:125])
                        statement['lines'][-1]['counterpartyCurrency'] = ''
                    else:
                        if line[22] == ' ':
                            statement['lines'][-1]['counterpartyNumber'] = rmspaces(line[10:22])
                            statement['lines'][-1]['counterpartyCurrency'] = rmspaces(line[23:26])
                        else:
                            statement['lines'][-1]['counterpartyNumber'] = rmspaces(line[10:44])
                            statement['lines'][-1]['counterpartyCurrency'] = rmspaces(line[44:47])
                        statement['lines'][-1]['counterpartyName'] = rmspaces(line[47:82])
                        statement['lines'][-1]['communication'] += rmspaces(line[82:125])
                else:
                    # movement data record 2.x (x != 1,2,3)
                    raise CodaParserException('R2006', _('\nMovement data records of type 2.%s are not supported ') % line[1])
            elif line[0] == '3':
                if line[1] == '1':
                    infoLine = {}
                    infoLine['entryDate'] = statement['lines'][-1]['entryDate']
                    infoLine['type'] = 'information'
                    infoLine['sequence'] = len(statement['lines']) + 1
                    infoLine['ref'] = rmspaces(line[2:10])
                    infoLine['transactionRef'] = rmspaces(line[10:31])
                    infoLine['transaction_type'] = line[31]
                    infoLine['transaction_family'] = rmspaces(line[32:34])
                    infoLine['transaction_code'] = rmspaces(line[34:36])
                    infoLine['transaction_category'] = rmspaces(line[36:39])
                    infoLine['communication'] = rmspaces(line[40:113])
                    statement['lines'].append(infoLine)
                elif line[1] == '2':
                    if infoLine['ref'] != rmspaces(line[2:10]):
                        raise CodaParserException('R3004', _('CODA parsing error on information data record 3.2, seq nr %s! Please report this issue via your OpenERP support channel.') % line[2:10])
                    statement['lines'][-1]['communication'] += rmspaces(line[10:100])
                elif line[1] == '3':
                    if infoLine['ref'] != rmspaces(line[2:10]):
                        raise CodaParserException('R3005', _('CODA parsing error on information data record 3.3, seq nr %s! Please report this issue via your OpenERP support channel.') % line[2:10])
                    statement['lines'][-1]['communication'] += rmspaces(line[10:100])
            elif line[0] == '4':
                    comm_line = {}
                    comm_line['type'] = 'communication'
                    comm_line['sequence'] = len(statement['lines']) + 1
                    comm_line['ref'] = rmspaces(line[2:10])
                    comm_line['communication'] = rmspaces(line[32:112])
                    statement['lines'].append(comm_line)
            elif line[0] == '8':
                # new balance record
                statement['debit'] = line[41]
                statement['paperSeqNumber'] = rmspaces(line[1:4])
                statement['balance_end_real'] = float(rmspaces(line[42:57])) / 1000
                statement['balance_end_realDate'] = time.strftime(date_format, time.strptime(rmspaces(line[57:63]), '%d%m%y'))
                if statement['debit'] == '1':    # 1=Debit
                    statement['balance_end_real'] = - statement['balance_end_real']
            elif line[0] == '9':
                statement['balanceMin'] = float(rmspaces(line[22:37])) / 1000
                statement['balancePlus'] = float(rmspaces(line[37:52])) / 1000
                if not statement.get('balance_end_real'):
                    statement['balance_end_real'] = statement['balance_start'] + statement['balancePlus'] - statement['balanceMin']
        return statements
        
           
def rmspaces(s):
    return " ".join(s.split())

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: 