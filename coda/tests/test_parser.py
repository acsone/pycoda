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
from coda.parser import Parser
from coda.statement import AmountSign, MovementRecordType
from nose.tools import eq_
import os

BASEPATH = os.path.dirname(__file__)

class TestParser(object):

    def testParser(self):
        parser = Parser()
        with open(os.path.join(BASEPATH, "Dummy_testbestand_coda_iban_v2_3.txt")) as f:
            content = f.read()
        statements = parser.parse(content)
        assert len(statements) == 1
        statement = statements[0]
        eq_(len(statement.movements), 32)
        eq_(len(statement.informations), 3)
        eq_(len(statement.free_comunications), 0)
        eq_(statement.creation_date, '2009-03-05')
        eq_(statement.separate_application, "00000")
        eq_(statement.version, "2")
        eq_(statement.acc_number, "BE86407051416150")
        eq_(statement.currency, "EUR")
        eq_(statement.description, "KBC-Bedrijfsrekening")
        eq_(statement.old_balance, 0.0)
        eq_(statement.old_balance_amount_sign, AmountSign.CREDIT)
        eq_(statement.old_balance_date, '2009-03-04')
        eq_(statement.account_holder_name, 'STORA ENSO LANGERBRUGGE NV')
        eq_(statement.paper_seq_number, "042")
        eq_(statement.coda_seq_number, "002")
        eq_(statement.new_balance, 0.0)
        eq_(statement.new_balance_amount_sign, AmountSign.CREDIT)
        eq_(statement.new_balance_date, '2009-03-05')
        eq_(statement.new_balance_paper_seq_number, "042")
        self._checkMovement(statement.movements[0])
        self._checkInformation(statement.informations[0])

    def _checkMovement(self, movement):
        eq_(movement.ref_move_detail, "0000")
        eq_(movement.transaction_ref, "SWJVZ0BN6 BKTBBNPOSKZ")
        eq_(movement.transaction_amount, 20.0)
        eq_(movement.transaction_amount_sign,  AmountSign.CREDIT)
        eq_(movement.transaction_type, "0")
        eq_(movement.transaction_date, '2009-03-05')
        eq_(movement.transaction_family, "04")
        eq_(movement.transaction_code, "50")
        eq_(movement.transaction_category, "000")
        eq_(movement.communication_is_structured, True)
        eq_(movement.communication_type, "114")
        eq_(movement.communication, "+++931/3843/84900+++ 2905172259460041")
        eq_(movement.entry_date, '2009-03-05')
        eq_(movement.type, MovementRecordType.NORMAL)
        eq_(movement.globalisation_code, 0)
        eq_(movement.payment_reference, '')
        eq_(movement.counterparty_bic, '')
        eq_(movement.counterparty_number, None)
        eq_(movement.counterparty_name, None)
        eq_(movement.counterparty_address, None)
        eq_(movement.counterparty_currency, None)

    def _checkInformation(self, information):
        eq_(information.ref, '00100001')
        eq_(information.transaction_ref, 'SWJVZ0BOX DOMUCVDIU01')
        eq_(information.transaction_type, '0')
        eq_(information.transaction_family, "05")
        eq_(information.transaction_code, "01")
        eq_(information.transaction_category, "000")
        eq_(information.communication, "001AMERICAN EXPRESS")
        
    def test_wrong_globalisation(self):
        """Test wrong globalisation
        
        Check that a globalisation line without the corresponding 'end globalisation'
        is considered as Normal 
        """
        parser = Parser()
        with open(os.path.join(BASEPATH, "Coda_v2_3_faulty_globalisation.txt")) as f:
            content = f.read()
        statements = parser.parse(content)
        assert len(statements) == 1
        statement = statements[0]
        eq_(len(statement.movements), 11)
        for mv in statement.movements:
            eq_(mv.type, MovementRecordType.NORMAL)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
