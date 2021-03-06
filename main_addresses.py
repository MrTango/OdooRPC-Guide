#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Dieses Skript importiert Hauptadressen aus einen CSV Datei
# This script imports main addresses from a CSV file
# Version 2.0.1
# Date 28.05.2018
##############################################################################
#
#    Python Script 3 for Odoo, Open Source Management Solution
#    Copyright (C) 2018-now Equitania Software GmbH(<http://www.equitania.de>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import csv
import get_country_id
import base_helper as helper
import time



# Verbindung
odoo = helper.odoo_connect()

RES_PARTNER = odoo.env['res.partner']
ACCOUNT_ACCOUNT = odoo.env['account.account']


_count = 0
_import_csv_file = "main_addresses.csv"

_csv_reader = csv.DictReader(open(helper.importcsv + _import_csv_file), delimiter=',')

_rows = list(_csv_reader)
_totalcount = len(_rows)

_csv_reader = csv.DictReader(open(helper.importcsv + _import_csv_file), delimiter=',')

# Bisherige Debitoren- und Kreditoren Nummern merken
# Wird nur benötigt, wenn Sie unser FIBU Module benutzen https://www.myodoo.de/finanzpaket
_old_payable_account_number = str(helper.get_ir_sequence_number_next_actual("partner.auto.payable"))
_old_receivable_account_number = str(helper.get_ir_sequence_number_next_actual("partner.auto.receivable"))

# Store start time
start_time = time.time()

# Perform any action like print a string
print("Printing this string takes ...")


for _main_addresses in _csv_reader:

    _do_import = _main_addresses["Import"].strip()
    if _do_import != "J":
        continue
        # Diesen Datensatz überspringen

    _partner_data = {}
    _is_company = None
    _company = _main_addresses["Unternehmen"].strip()
    if _company == "J":
        _partner_data['is_company'] = True
        _is_company = True
    else:
        _partner_data['is_company'] = False
        _is_company = False

    # Kundennummer
    _customerno = _main_addresses["Kundennr"]
    if _customerno != None and _customerno != "":
        _partner_data['customer_number'] = _customerno
        _partner_data['customer'] = True
    else:
        _partner_data['customer'] = False
        _customerno = None

    _supplierno = _main_addresses["Lieferantennr"]
    if _supplierno != None and _supplierno != "":
        _partner_data['supplier_number'] = _supplierno
        _partner_data['supplier'] = True
    else:
        _partner_data['supplier'] = False
        _supplierno = None

    # Logo
    _logo = _main_addresses["Logo"].strip()
    if _logo != None and _logo != "":
        _partner_data['image'] = helper.get_picture(helper.importimages + _logo)

    # Name 1
    _name1 = _main_addresses["Firmenname 1"].strip()
    if _name1 != None and _name1 != "":
        _partner_data['name'] = _name1

    # Nach bestehendem Kunden suchen
    if _supplierno == None and _customerno != None:
        _partner_id = RES_PARTNER.search([('name', '=', _name1), ('customer_number', '=', _customerno)])
    elif _supplierno != None and _customerno == None:
        _partner_id = RES_PARTNER.search([('name', '=', _name1), ('supplier_number', '=', _supplierno)])
    elif _supplierno != None and _customerno != None:
        _partner_id = RES_PARTNER.search([('name', '=', _name1), ('supplier_number', '=', _supplierno), ('customer_number', '=', _customerno)])

    # Name 2 / Vorname / Anrede
    _name2 = _main_addresses["Firmenname 2"].strip()
    if _name2 != None and _name2 != "":
        if _is_company:
            _partner_data['eq_name2'] = _name2
        else:
            _partner_data['eq_firstname'] = _name2
            _title = _main_addresses["Anrede"].strip()
            if _title != None and _title != "":
                _title_id = helper.get_res_partner_title_id(_title)
                if _title_id != 0 and _title_id != None:
                    _partner_data['title'] = _title_id

    # Name 3
    _name3 = _main_addresses["Firmenname 3"].strip()
    if _name3 != None and _name3 != "":
        _partner_data['eq_name3'] = _name3

    # Land / Bundesland/Region
    _land = _main_addresses["Land"].strip()
    _land_id = get_country_id.get_odoo_country_id(_land)
    if _land_id != 0:
        _partner_data['country_id'] = _land_id
        _state = _main_addresses["Region"].strip()
        if _state != None and _state != "":
            _land_id = get_country_id.get_odoo_country_id(_land)
            _state_id = helper.get_state_id(_land_id,_state)
            if _state_id != 0 and _state_id != None:
                _partner_data['state_id'] = _state_id

    # Strasse
    _street = _main_addresses["Strasse"].strip()
    if _street != None and _street != "":
        _partner_data['street'] = _street

    # Hausnummer
    _houseno = _main_addresses["Hausnummer"].strip()
    if _houseno != None and _houseno != "":
        _partner_data['eq_house_no'] = _houseno

    # PLZ
    _zipcode = _main_addresses["PLZ"].strip()
    if _zipcode != None and _zipcode != "":
        _partner_data['zip'] = _zipcode

    # Ort
    _city = _main_addresses["Ort"].strip()
    if _city != None and _city != "":
        _partner_data['city'] = _city

    # Telefon
    _phone = _main_addresses["Telefon 1"].strip()
    if _phone != None and _phone != "":
        _partner_data['phone'] = _phone

    # Telefon 2
    _phone2 = _main_addresses["Telefon 2"].strip()
    if _phone2 != None and _phone2 != "":
        _partner_data['eq_phone2'] = _phone2

    # Fax
    _fax = _main_addresses["Telefax"].strip()
    if _fax != None and _fax != "":
        _partner_data['fax'] = _fax

    # Email
    _email = _main_addresses["E-Mail 1"].strip()
    if _email != None and _email != "":
        _partner_data['email'] = _email

    # Email 2
    _email2 = _main_addresses["E-Mail 1"].strip()
    if _email2 != None and _email2 != "":
        _partner_data['eq_email2'] = _email2

    # Homepage
    _homepage = _main_addresses["Homepage"].strip()
    if _homepage != None and _homepage != "":
        _partner_data['website'] = _homepage

    # UST ID
    _vat = _main_addresses["USTID"].strip()
    if _vat != None and _vat != "":
        _partner_data['vat'] = _vat


    # ---------------------------Schlagwoerter--------------------------------------------------
    _category_id = False
    _category_name = _main_addresses["Kategorie"].strip()
    if len(_category_name) != 0 and _category_name != None:
        _category_id = helper.get_res_partner_category_id(_category_name)
        if _category_id != 0 and _category_id != None:
            _partner_data['category_id'] = [(6, 0, [_category_id])]

    if len(_partner_id) == 0:
        # Kunden/Debitoren Zähler setzen
        if _customerno != None and _customerno != "":
            helper.set_ir_sequence_number_next_actual("partner.auto.receivable", _customerno)
        # Lieferanten/Kreditoren Zähler setzen
        if _supplierno != None and _supplierno != "":
            helper.set_ir_sequence_number_next_actual("partner.auto.payable", _supplierno)
        _res_partner_id = RES_PARTNER.create(_partner_data)
        _importtype = " importiert "
        _res_partner = RES_PARTNER.browse(_res_partner_id)
        _temp_customer_number = _res_partner.customer_number
    else:
        _res_partner = RES_PARTNER.browse(_partner_id)
        _res_partner.write(_partner_data)
        _importtype = " aktualisiert "

    _count += 1
    print ("Adresse mit KD-Nr. " + str(_customerno) + " / Lieferantennr. " + str(_supplierno) + " / " + _name1 + _importtype + " - bereits " + str(_count) + " von " + str(_totalcount) + " Positionen..")

# Temporär Debitoren- und Kreditoren Nummern zurücksetzen
helper.set_ir_sequence_number_next_actual("partner.auto.payable",_old_payable_account_number)
helper.set_ir_sequence_number_next_actual("partner.auto.receivable",_old_receivable_account_number)

# Store end time
end_time = time.time()

# Calculate the execution time and print the result
print("%.10f seconds" % (end_time - start_time))

print ("Fertig!")
