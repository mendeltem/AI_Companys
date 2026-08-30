# -*- coding: utf-8 -*-
"""Traegt den inneren Wert in die Seite ein - auf jede Firmenseite.

Der Eingriff ist bewusst klein und wiederholbar: ein eigener JSON-Block neben
den vorhandenen, eine Kennzahlkachel, ein Rechenweg hinter dem Klick, dazu die
Texte in drei Sprachen. Alles ueber Marker, damit derselbe Aufruf morgen
dieselbe Stelle findet und nichts doppelt einfuegt.

    python werkzeuge/seite.py            # eintragen und pruefen
    python werkzeuge/seite.py --pruefen  # nur sagen, was passieren wuerde
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import berichte as b                                            # noqa: E402
import wert as W                                                # noqa: E402

MARKE = "/* wertung: eingetragen */"

GRUPPEN_ALT = '  const kz=[\n    [T(\'kz_kurs\'), kursF(e.kurs,w), e.kursdatum, null],\n    [T(\'kz_marktkap\'), gross(e.marktkap_usd,\'USD\'), gross(e.marktkap,w), \'marktkap\'],\n    [T(\'kz_kgv_ttm\'), nf(e.kgv_ttm,1), T(\'kz_eps\')+\' \'+nf(inUsd(e.eps_ttm,w),2)+\' USD\', \'kgv_ttm\'],\n    [T(\'kz_kgv_q4x\'), nf(e.kgv_q4x,1), T(\'kz_letztes_q\')+\' \'+nf(inUsd(e.eps_q,w),2)+\' USD\', \'kgv_q4x\'],\n    [T(\'kz_kgv_q4x_op\'), nf(e.kgv_q4x_op,1), T(\'kz_op_q\')+\' \'+gross(e.op_q,w), \'kgv_q4x_op\'],\n    [T(\'kz_kuv\'), nf(e.kuv,1), T(\'kz_umsatz\')+\' \'+gross(e.umsatz_ttm_usd,\'USD\'), \'kuv\'],\n    [T(\'kz_umsatz_yoy\'), pf(e.umsatz_yoy), T(\'kz_letztes_q\'), null],\n    [T(\'kz_kurs3j\'), pf(e.rendite_3j,0), T(\'kz_kurs1j\')+\' \'+pf(e.rendite_1j,0), null],\n  ];\n  let kzh=\'\';\n  for(const [t,v,s,art] of kz){\n    const geht = art && erklaerung(art, k);\n    kzh += geht\n      ? `<div class="kz klickbar" tabindex="0" role="button" data-erkl="${art}"\n           title="${T(\'erkl_oeffnen\')}"><small>${t}</small><b>${v}</b><em>${s}</em></div>`\n      : `<div class="kz"><small>${t}</small><b>${v}</b><em>${s}</em></div>`;\n  }\n'

GRUPPEN_NEU = '  /* kennzahl-gruppen */\n  // Drei Gruppen statt einer Reihe. Rendite und KGV stehen in derselben\n  // Kachel, weil sie dieselbe Zahl sind - einmal als Prozentsatz im Jahr,\n  // einmal als Zahl der Jahre bis zur Amortisation. Der Kursverlauf ist keine\n  // eigene Kennzahl mehr, sondern liegt hinter dem Klick auf den Kurs.\n  const wv = WERT[k];\n  const ekWert = (wv && wv.wert!=null) ? wv.unternehmenswert - wv.nettoschulden : null;\n  const kgvText = (v)=> v==null ? \'\' : \' \\u00b7 \' + T(\'kz_kgv_kurz\') + \' \' + nf(v,1);\n  const opQ = opJeAktie(e,false), opV = opJeAktie(e,true);\n  const kgvOpV = (opV!=null && e.kurs) ? e.kurs/opV : null;\n\n  const kzGruppen=[\n    {titel:T(\'gr_preis\'), text:T(\'gr_preis_t\'), kacheln:[\n      [T(\'kz_kurs\'), kursF(e.kurs,w), e.kursdatum, \'kurs\'],\n      [T(\'kz_marktkap\'), gross(e.marktkap,w),\n       ekWert!=null\n         ? T(\'kz_wert\')+\' \'+gross(ekWert, wv.waehrung||w)+\' \\u00b7 \'+T(\'kz_wert_verh\')+\' \'+nf(e.marktkap_usd/inUsd(ekWert, wv.waehrung||w),2)\n         : (wv ? (wv.grund||\'\').split(\' - \')[0] : \'\'),\n       ekWert!=null ? \'wert\' : \'marktkap\'],\n      [T(\'kz_kuv\'), nf(e.kuv,1), T(\'kz_umsatz\')+\' \'+gross(e.umsatz_ttm_usd,\'USD\'), \'kuv\'],\n    ]},\n    {titel:T(\'gr_ertrag\'), text:T(\'gr_ertrag_t\'), kacheln:[\n      [T(\'kz_rendite_q\'),\n       e.eps_q!=null ? pf(rendite(e.eps_q*4, e.kurs),1) : \'\\u2013\',\n       (e.eps_q!=null ? nf(inUsd(e.eps_q,w),2)+\' USD \\u00d7 4\' : T(\'kz_rendite_verlust\'))\n         + kgvText(e.kgv_q4x), \'kgv_q4x\'],\n      [T(\'kz_rendite_ttm\'),\n       e.eps_ttm!=null ? pf(rendite(e.eps_ttm, e.kurs),1) : \'\\u2013\',\n       (e.eps_ttm!=null ? nf(inUsd(e.eps_ttm,w),2)+\' USD\' : T(\'kz_rendite_verlust\'))\n         + kgvText(e.kgv_ttm), \'kgv_ttm\'],\n      [T(\'kz_rendite_op_q\'),\n       opQ!=null ? pf(rendite(opQ*4, e.kurs),1) : \'\\u2013\',\n       (opQ!=null ? nf(inUsd(opQ,w),2)+\' USD \\u00d7 4\' : T(\'kz_rendite_verlust\'))\n         + kgvText(e.kgv_q4x_op), \'kgv_q4x_op\'],\n      [T(\'kz_rendite_op_ttm\'),\n       opV!=null ? pf(rendite(opV, e.kurs),1) : \'\\u2013\',\n       (opV!=null ? nf(inUsd(opV,w),2)+\' USD\' : T(\'kz_rendite_verlust\'))\n         + kgvText(kgvOpV), null],\n    ]},\n    {titel:T(\'gr_wachstum\'), text:T(\'gr_wachstum_t\'), kacheln:[\n      [T(\'kz_umsatz_yoy\'), pf(e.umsatz_yoy), T(\'kz_letztes_q\'), null],\n    ]},\n  ];\n\n  let kzh=\'\';\n  for(const g of kzGruppen){\n    let innen=\'\';\n    for(const [t,v,s,art] of g.kacheln){\n      const geht = art && erklaerung(art, k);\n      innen += geht\n        ? `<div class="kz klickbar" tabindex="0" role="button" data-erkl="${art}"\n             title="${T(\'erkl_oeffnen\')}"><small>${t}</small><b>${v}</b><em>${s}</em></div>`\n        : `<div class="kz"><small>${t}</small><b>${v}</b><em>${s}</em></div>`;\n    }\n    kzh += `<section class="kzgruppe"><h4>${g.titel}</h4><p>${g.text}</p>\n            <div class="kennzahlen">${innen}</div></section>`;\n  }\n  /* ende kennzahl-gruppen */\n'

RAHMEN_ALT = '  <div class="abschnitt"><div class="kennzahlen">${kzh}</div>'
RAHMEN_NEU = '  <div class="abschnitt"><div class="kzgruppen">${kzh}</div>'

CSS_MARKE = '/* kzgruppen */'
CSS = '\n/* kzgruppen */\n.kzgruppen{display:flex;flex-direction:column;gap:22px}\n.kzgruppe h4{font-family:var(--disp);font-size:15px;font-weight:600;letter-spacing:.01em;\n             margin:0 0 3px;color:var(--tinte)}\n.kzgruppe > p{margin:0 0 9px;font-size:12.5px;line-height:1.5;color:var(--gedaempft);\n              max-width:78ch}\n'


TEXTE = {
    "gr_preis": {
        "de": "Preis und Wert",
        "en": "Price and value",
        "mn": "Үнэ ба үнэ цэнэ",
    },
    "gr_preis_t": {
        "de": "Was der Markt fuer die Firma verlangt \u2014 und was dieselbe Firma wert ist, "
              "wenn man sie aus Cashflow und Investitionen rechnet statt aus dem Kurs.",
        "en": "What the market charges for the company \u2014 and what the same company is "
              "worth when calculated from cash flow and capital expenditure rather than "
              "from the share price.",
        "mn": "Зах зээл компанид ямар үнэ тавьж байгаа, мөн мөнгөн урсгалаас тооцвол "
              "ямар үнэ цэнэтэй болох.",
    },
    "gr_ertrag": {
        "de": "Was die Firma verdient",
        "en": "What the company earns",
        "mn": "Компани юу олж байна",
    },
    "gr_ertrag_t": {
        "de": "Als Rendite auf den Kaufpreis gelesen, unabhaengig von der Stueckzahl: "
              "bei einer Aktie dieselbe Zahl wie bei hundert. Daneben dieselbe Aussage als "
              "KGV, also die Zahl der Jahre. Netto enthaelt Beteiligungen, Waehrungseffekte "
              "und Einmaliges; operativ nur das Geschaeft selbst.",
        "en": "Read as a yield on the purchase price, independent of the number of shares: "
              "the same figure for one share as for a hundred. Beside it the same statement "
              "as a P/E, that is the number of years. Net includes investments, currency "
              "effects and one-offs; operating only the business itself.",
        "mn": "Худалдан авсан үнэ дээрх өгөөж болгон уншина. Хажууд нь ижил утгыг P/E "
              "буюу жилийн тоогоор. Цэвэр нь нэг удаагийн зүйлсийг агуулна, үйл "
              "ажиллагааны нь зөвхөн бизнесийг.",
    },
    "gr_wachstum": {
        "de": "Wie schnell es waechst",
        "en": "How fast it grows",
        "mn": "Хэр хурдан өсч байна",
    },
    "gr_wachstum_t": {
        "de": "Der Umsatz des letzten Quartals gegen das gleiche Quartal des Vorjahres. "
              "Er entscheidet, ob die Rendite oben in einem Jahr hoeher oder niedriger steht.",
        "en": "Revenue of the latest quarter against the same quarter a year earlier. It "
              "decides whether the yield above will be higher or lower a year from now.",
        "mn": "Сүүлийн улирлын орлого өмнөх оны мөн үетэй харьцуулбал.",
    },
    "kz_kgv_kurz": {
        "de": "KGV",
        "en": "P/E",
        "mn": "P/E",
    },
    "kurs_frage": {
        "de": "Was hat die Aktie gekostet, und wie hat sie sich bewegt?",
        "en": "What does the share cost, and how has it moved?",
        "mn": "Хувьцаа хэдэн төгрөг байсан, хэрхэн хөдөлсөн бэ?",
    },
    "kurs_s1": {
        "de": "Schlusskurs am Datenstand, von der Heimatboerse",
        "en": "Closing price at the data date, from the home exchange",
        "mn": "Өгөгдлийн огнооны хаалтын ханш",
    },
    "kurs_s2": {
        "de": "Veraenderung ueber ein Jahr",
        "en": "Change over one year",
        "mn": "Нэг жилийн өөрчлөлт",
    },
    "kurs_s3": {
        "de": "Veraenderung ueber drei Jahre",
        "en": "Change over three years",
        "mn": "Гурван жилийн өөрчлөлт",
    },
    "kurs_bedeutet": {
        "de": "Der Kurs sagt, was andere zuletzt gezahlt haben, nicht was die Firma wert "
              "ist. Die beiden Zahlen daneben sind Vergangenheit und keine Fortschreibung.",
        "en": "The price says what others last paid, not what the company is worth. The two "
              "figures beside it are the past, not a projection.",
        "mn": "Ханш нь бусад хүмүүс сүүлд хэд төлснийг хэлнэ, компанийн үнэ цэнийг биш.",
    },
    "kurs_nicht": {
        "de": "Kein Einstiegssignal. Ein Kurs, der drei Jahre gestiegen ist, sagt nichts "
              "darueber, was er im vierten tut.",
        "en": "Not an entry signal. A price that has risen for three years says nothing "
              "about what it does in the fourth.",
        "mn": "Худалдан авах дохио биш.",
    },
    "kz_wert": {
        "de": "Innerer Wert",
        "en": "Intrinsic value",
        "mn": "\u0411\u043e\u0434\u0438\u0442 \u04af\u043d\u044d \u0446\u044d\u043d\u044d",
    },
    "kz_wert_verh": {
        "de": "Kurs \u00f7 Wert",
        "en": "price \u00f7 value",
        "mn": "\u0425\u0430\u043d\u0448 \u00f7 \u04af\u043d\u044d \u0446\u044d\u043d\u044d",
    },
    "wert_frage": {
        "de": "Was ist die Firma wert, wenn man den Kurs nicht kennt?",
        "en": "What is the company worth if you do not look at the share price?",
        "mn": "\u0425\u0430\u043d\u0448\u044b\u0433 \u0445\u0430\u0440\u0430\u0445\u0433\u04af\u0439\u0433\u044d\u044d\u0440 "
              "\u043a\u043e\u043c\u043f\u0430\u043d\u0438 \u044f\u043c\u0430\u0440 \u04af\u043d\u044d\u0442\u044d\u0439 \u0432\u044d?",
    },
    "wert_s1": {
        "de": "Freier Cashflow als Ausgangspunkt: operativer Cashflow minus Investitionen, "
              "aus den Jahresabschluessen",
        "en": "Free cash flow as the starting point: operating cash flow minus capital "
              "expenditure, from the annual filings",
        "mn": "\u0427\u04e9\u043b\u04e9\u04e9\u0442 \u043c\u04e9\u043d\u0433\u04e9\u043d \u0443\u0440\u0441\u0433\u0430\u043b: "
              "\u04af\u0439\u043b \u0430\u0436\u0438\u043b\u043b\u0430\u0433\u0430\u0430\u043d\u044b \u0443\u0440\u0441\u0433\u0430\u043b "
              "\u0445\u0430\u0441\u0430\u0445 \u043a\u0430\u043f\u0438\u0442\u0430\u043b \u0437\u0430\u0440\u0434\u0430\u043b",
    },
    "wert_s2": {
        "de": "Zehn Jahre fortgeschrieben, das Anfangswachstum klingt auf drei Prozent ab",
        "en": "Projected ten years, the initial growth fading to three per cent",
        "mn": "\u0410\u0440\u0432\u0430\u043d \u0436\u0438\u043b\u044d\u044d\u0440 \u0442\u04e9\u0441\u04e9\u04e9\u043b\u0436, "
              "\u04e9\u0441\u04e9\u043b\u0442 \u0433\u0443\u0440\u0432\u0430\u043d \u0445\u0443\u0432\u044c \u0440\u0443\u0443 \u0431\u0443\u0443\u0440\u043d\u0430",
    },
    "wert_s3": {
        "de": "Abgezinst mit zehn Prozent, dazu der Endwert fuer die Zeit danach",
        "en": "Discounted at ten per cent, plus the terminal value for everything after",
        "mn": "\u0410\u0440\u0432\u0430\u043d \u0445\u0443\u0432\u0438\u0430\u0440 \u0445\u04af\u04af\u0433\u044d\u044d\u0440 "
              "\u0445\u04e9\u0440\u0432\u04af\u04af\u043b\u0436, \u0434\u044d\u044d\u0440 \u043d\u044c \u044d\u0446\u0441\u0438\u0439\u043d \u04af\u043d\u044d \u0446\u044d\u043d\u044d",
    },
    "wert_s4": {
        "de": "Nettoschulden abgezogen, durch die Aktienzahl geteilt",
        "en": "Net debt deducted, divided by the share count",
        "mn": "\u0426\u044d\u0432\u044d\u0440 \u04e9\u0440\u0438\u0439\u0433 \u0445\u0430\u0441\u0430\u0436, "
              "\u0445\u0443\u0432\u044c\u0446\u0430\u0430\u043d\u044b \u0442\u043e\u043e\u043d\u0434 \u0445\u0443\u0432\u0430\u0430\u043d\u0430",
    },
    "wert_bedeutet": {
        "de": "Der Markt zahlt das {x}-fache dessen, was diese Rechnung ergibt. Ueber "
              "eins heisst: teurer als die Rechnung, unter eins: billiger. {y} Prozent "
              "des Ergebnisses stecken im Endwert, also in der Annahme ueber Jahr elf "
              "und danach.",
        "en": "The market pays {x} times what this calculation produces. Above one means "
              "dearer than the calculation, below one cheaper. {y} per cent of the result "
              "sits in the terminal value, that is in the assumption about year eleven "
              "and beyond.",
        "mn": "\u0417\u0430\u0445 \u0437\u044d\u044d\u043b \u044d\u043d\u044d \u0442\u043e\u043e\u0446\u043e\u043e\u043d\u043e\u043e\u0441 "
              "{x} \u0434\u0430\u0445\u0438\u043d \u0438\u0445 \u0442\u04e9\u043b\u0436 \u0431\u0430\u0439\u043d\u0430. "
              "\u04ae\u0440 \u0434\u04af\u043d\u0433\u0438\u0439\u043d {y} \u0445\u0443\u0432\u044c \u043d\u044c "
              "\u044d\u0446\u0441\u0438\u0439\u043d \u04af\u043d\u044d \u0446\u044d\u043d\u044d\u0434 \u0431\u0430\u0439\u043d\u0430.",
    },
    "wert_nicht": {
        "de": "Keine Prognose und kein Kursziel. Der Abzinssatz ist gesetzt, nicht "
              "gemessen: Ein Lehrbuch-WACC zoege sein Beta aus der Kursreihe, dann haenge "
              "der angeblich kursunabhaengige Wert wieder am Kurs. Wer die Huerde auf acht "
              "oder zwoelf Prozent stellt, bekommt eine deutlich andere Zahl.",
        "en": "Not a forecast and not a price target. The discount rate is set, not "
              "measured: a textbook WACC would take its beta from the price series, and "
              "then the supposedly price-independent value would hang on the price again. "
              "Set the hurdle at eight or twelve per cent and the number changes markedly.",
        "mn": "\u0422\u0430\u0430\u043c\u0430\u0433\u043b\u0430\u043b \u0431\u0438\u0448, "
              "\u0437\u043e\u0440\u0438\u043b\u0442\u043e\u0442 \u0445\u0430\u043d\u0448 \u0431\u0438\u0448. "
              "\u0425\u04af\u04af\u0433\u0438\u0439\u043d \u0442\u04af\u0432\u0448\u0438\u043d \u043d\u044c "
              "\u0445\u044d\u043c\u0436\u0438\u0433\u0434\u0441\u044d\u043d \u0431\u0438\u0448, \u0442\u043e\u0433\u0442\u043e\u043e\u0441\u043e\u043d.",
    },
    "wert_guthaben": {
        "de": "Nettoguthaben: mehr Geld als Schulden, deshalb addiert",
        "en": "Net cash: more money than debt, therefore added",
        "mn": "Цэвэр бэлэн мөнгө: өрөөс их тул нэмнэ",
    },
    "wert_schulden": {
        "de": "Nettoschulden: mehr Schulden als Geld, deshalb abgezogen",
        "en": "Net debt: more debt than money, therefore deducted",
        "mn": "Цэвэр өр: бэлэн мөнгөнөөс их тул хасна",
    },
    "kz_rendite_q": {
        "de": "Gewinnrendite netto, letztes Quartal",
        "en": "Earnings yield, net, latest quarter",
        "mn": "Цэвэр ашгийн өгөөж, сүүлийн улирал",
    },
    "kz_rendite_ttm": {
        "de": "Gewinnrendite netto, vier Quartale",
        "en": "Earnings yield, net, four quarters",
        "mn": "Цэвэр ашгийн өгөөж, дөрвөн улирал",
    },
    "kz_rendite_op_q": {
        "de": "Gewinnrendite operativ, letztes Quartal",
        "en": "Earnings yield, operating, latest quarter",
        "mn": "Үйл ажиллагааны өгөөж, сүүлийн улирал",
    },
    "kz_rendite_op_ttm": {
        "de": "Gewinnrendite operativ, vier Quartale",
        "en": "Earnings yield, operating, four quarters",
        "mn": "Үйл ажиллагааны өгөөж, дөрвөн улирал",
    },
    "kz_rendite_q_sub": {
        "de": "Nettogewinn je Aktie {x} × 4, geteilt durch den Kurs",
        "en": "net profit per share {x} × 4, divided by the price",
        "mn": "нэгж хувьцааны цэвэр ашиг {x} × 4, ханшид хуваасан",
    },
    "kz_rendite_ttm_sub": {
        "de": "Nettogewinn je Aktie {x}, geteilt durch den Kurs",
        "en": "net profit per share {x}, divided by the price",
        "mn": "нэгж хувьцааны цэвэр ашиг {x}, ханшид хуваасан",
    },
    "kz_rendite_op_q_sub": {
        "de": "operatives Ergebnis je Aktie {x} × 4, geteilt durch den Kurs",
        "en": "operating profit per share {x} × 4, divided by the price",
        "mn": "нэгж хувьцааны үйл ажиллагааны ашиг {x} × 4, ханшид хуваасан",
    },
    "kz_rendite_op_ttm_sub": {
        "de": "operatives Ergebnis je Aktie {x}, geteilt durch den Kurs",
        "en": "operating profit per share {x}, divided by the price",
        "mn": "нэгж хувьцааны үйл ажиллагааны ашиг {x}, ханшид хуваасан",
    },
    "kz_rendite_verlust": {
        "de": "Verlust, keine Rendite",
        "en": "loss, no yield",
        "mn": "алдагдалтай тул өгөөжгүй",
    },
    "wert_leer": {
        "de": "nicht berechenbar",
        "en": "not calculable",
        "mn": "\u0442\u043e\u043e\u0446\u043e\u043e\u043b\u043e\u0445 \u0431\u043e\u043b\u043e\u043c\u0436\u0433\u04af\u0439",
    },
}

# --- 0. Rechenhilfe fuer die Gewinnrendite ---------------------------------
# Der Kehrwert des KGV, aber als Rendite gelesen: Wieviel Prozent des
# eingesetzten Kurses verdient die Firma im Jahr? Das laesst sich unmittelbar
# gegen eine Anleiherendite halten und gegen die zehn Prozent, mit denen der
# innere Wert abgezinst wird. Ein Verlust ergibt eine negative Rendite - die
# wird gezeigt, nicht versteckt, denn sie ist eine richtige Aussage.
HILFEN = """
const rendite = (eps, kurs)=> (eps==null || !kurs) ? null : eps/kurs*100;
// Operatives Ergebnis je Aktie. Der Nettogewinn traegt Beteiligungs-
// bewertungen, Waehrungseffekte und Einmaliges mit; das operative Ergebnis
// ist das, was das Geschaeft selbst abwirft. Beide Renditen nebeneinander
// zeigen, wie viel davon aus dem laufenden Betrieb kommt.
const opJeAktie = (e, vier)=>{
  const q=e.quartale, n=e.aktien_zahl;
  if(!n || !q || !q.length) return null;
  if(!vier) return q[0].operativ==null ? null : q[0].operativ/n;
  if(q.length<4) return null;
  let s=0;
  for(const z of q.slice(0,4)){ if(z.operativ==null) return null; s+=z.operativ; }
  return s/n;
};
"""

# --- 1. Kennzahlkachel ------------------------------------------------------
UMSATZ_ALT = "    [T('kz_umsatz_yoy'), pf(e.umsatz_yoy), T('kz_letztes_q'), null],\n"
UMSATZ_NEU = ("    [T('kz_rendite_q'),\n"
              "     e.eps_q!=null ? pf(rendite(e.eps_q*4, e.kurs),1) : '\\u2013',\n"
              "     e.eps_q!=null\n"
              "       ? T('kz_rendite_q_sub').split('{x}').join(nf(e.eps_q,2)+' '+w)\n"
              "       : T('kz_rendite_verlust'), null],\n"
              "    [T('kz_rendite_ttm'),\n"
              "     e.eps_ttm!=null ? pf(rendite(e.eps_ttm, e.kurs),1) : '\\u2013',\n"
              "     e.eps_ttm!=null\n"
              "       ? T('kz_rendite_ttm_sub').split('{x}').join(nf(e.eps_ttm,2)+' '+w)\n"
              "       : T('kz_rendite_verlust'), null],\n"
              "    [T('kz_rendite_op_q'),\n"
              "     opJeAktie(e,false)!=null ? pf(rendite(opJeAktie(e,false)*4, e.kurs),1) : '\\u2013',\n"
              "     opJeAktie(e,false)!=null\n"
              "       ? T('kz_rendite_op_q_sub').split('{x}').join(nf(opJeAktie(e,false),2)+' '+w)\n"
              "       : T('kz_rendite_verlust'), null],\n"
              "    [T('kz_rendite_op_ttm'),\n"
              "     opJeAktie(e,true)!=null ? pf(rendite(opJeAktie(e,true), e.kurs),1) : '\\u2013',\n"
              "     opJeAktie(e,true)!=null\n"
              "       ? T('kz_rendite_op_ttm_sub').split('{x}').join(nf(opJeAktie(e,true),2)+' '+w)\n"
              "       : T('kz_rendite_verlust'), null],\n")

KACHEL_ALT = "    [T('kz_kurs'), kursF(e.kurs,w), e.kursdatum, null],\n"
KACHEL_NEU = ("    [T('kz_wert'),\n"
              "     WERT[k] && WERT[k].wert!=null ? kursF(WERT[k].wert, WERT[k].waehrung||w) : '\\u2013',\n"
              "     WERT[k] && WERT[k].wert!=null\n"
              "       ? T('kz_wert_verh')+' '+nf(e.kurs/WERT[k].wert,2)\n"
              "       : (WERT[k] ? (WERT[k].grund||'').split(' - ')[0] : T('wert_leer')),\n"
              "     WERT[k] && WERT[k].wert!=null ? 'wert' : null],\n")

# --- 2. Rechenweg hinter dem Klick -----------------------------------------
ERKL = """  else if(art==='kurs'){
    // Der Kursverlauf war eine eigene Kachel und hat dort Platz beansprucht,
    // ohne eine Kennzahl zu sein. Er gehoert zum Kurs, also hierher.
    titel=T('kz_kurs'); frage=T('kurs_frage');
    schritte=[
      {text:T('kurs_s1'), rechnung:kursF(e.kurs,w), zusatz:e.kursdatum+' \\u00b7 '+e.symbol+' \\u00b7 '+e.boerse},
      {text:T('kurs_s2'), rechnung:pf(e.rendite_1j,0)},
      {text:T('kurs_s3'), rechnung:pf(e.rendite_3j,0)}];
    ergebnis=kursF(e.kurs,w);
    bedeutet=T('kurs_bedeutet');
    nicht=T('kurs_nicht');
  }
  else if(art==='wert'){
    const v=WERT[k];
    if(!v || v.wert==null) return null;
    const wv=v.waehrung||w;
    titel=T('kz_wert'); frage=T('wert_frage');
    schritte=[
      {text:T('wert_s1'), rechnung:`${gross(v.fcf_basis,wv)}`,
       zusatz:Object.keys(v.fcf||{}).sort().map(j=>j+': '+gross(v.fcf[j],wv)).join('   ')},
      {text:T('wert_s2'), rechnung:`${pf(100*v.wachstum,1)}  \\u2192  ${pf(3,0)}`},
      {text:T('wert_s3'), rechnung:`${gross(v.unternehmenswert,wv)}`},
      {text:T('wert_s4'),
       // Klammern, weil ohne sie Punkt vor Strich gilt und die Zeile etwas
       // anderes behauptet als die Rechnung. Und bei Nettoguthaben wird
       // addiert statt zweimal minus zu schreiben.
       rechnung:`(${gross(v.unternehmenswert,wv)}  ${v.nettoschulden<0?'+':'\\u2212'}  ${gross(Math.abs(v.nettoschulden),wv)})  \\u00f7  ${nf(v.aktien/1e6,0)} Mio  =  ${kursF(v.wert,wv)}`,
       zusatz:v.nettoschulden<0?T('wert_guthaben'):T('wert_schulden')}];
    ergebnis=kursF(v.wert,wv);
    bedeutet=T('wert_bedeutet').split('{x}').join(nf(e.kurs/v.wert,2))
             .split('{y}').join(nf(100*v.endwertanteil,0));
    nicht=T('wert_nicht');
  }
"""


def _block(s, name, anker, inhalt):
    """Einen Abschnitt zwischen zwei Marken setzen oder ersetzen.

    Beim ersten Lauf wird er hinter den Anker gesetzt, bei jedem weiteren
    ersetzt. Ohne das Ersetzen bleibt eine alte Fassung stehen, sobald sie
    einmal im Repository liegt - genau der Fall, in dem auf der Seite ein
    Platzhalter statt einer Zahl erscheint.
    """
    auf, zu = "    /* %s */\n" % name, "    /* ende %s */\n" % name
    neu = auf + inhalt + zu
    if auf in s:
        return re.sub(re.escape(auf) + ".*?" + re.escape(zu), lambda _: neu, s,
                      count=1, flags=re.S), "ersetzt"
    if anker not in s:
        sys.exit("Ankerstelle fuer %s nicht gefunden - die Seite hat sich geaendert." % name)
    return s.replace(anker, anker + neu, 1), "eingefuegt"


def eintragen(pruefen=False):
    pfad = os.path.join(b.WURZEL, "nvidia-oekosystem.html")
    s = open(pfad, encoding="utf-8").read()
    daten = json.load(open(b._pfad("wert.json"), encoding="utf-8"))
    mit = sum(1 for v in daten.values() if v.get("wert") is not None)
    schritte = []

    # Datenblock: ersetzen wenn da, sonst hinter den letzten JSON-Block setzen.
    block = '<script id="wertung" type="application/json">%s</script>' % json.dumps(
        daten, ensure_ascii=False, separators=(",", ":"))
    if 'id="wertung"' in s:
        s = re.sub(r'<script id="wertung" type="application/json">.*?</script>',
                   lambda _: block, s, count=1, flags=re.S)
        schritte.append("Datenblock ersetzt")
    else:
        anker = re.search(r'(<script id="operativ" type="application/json">.*?</script>\n)', s, re.S)
        s = s[:anker.end()] + block + "\n" + s[anker.end():]
        schritte.append("Datenblock eingefuegt")

    if "const WERT" not in s:
        s = s.replace("const OP = JSON.parse(document.getElementById('operativ').textContent);",
                      "const OP = JSON.parse(document.getElementById('operativ').textContent);\n"
                      "const WERT = JSON.parse(document.getElementById('wertung').textContent);", 1)
        schritte.append("WERT verdrahtet")

    if "const rendite" not in s:
        s = s.replace("const WERT = JSON.parse(document.getElementById('wertung').textContent);",
                      "const WERT = JSON.parse(document.getElementById('wertung').textContent);"
                      + HILFEN, 1)
        schritte.append("Renditehilfe eingefuegt")

    # Beide Kachelbloecke stehen zwischen Marken und werden bei jedem Lauf
    # ersetzt, nicht nur beim ersten. Sonst bleibt eine einmal eingetragene
    # Fassung fuer immer stehen, waehrend die Texte daneben schon die neuen
    # sind - dann steht ein Platzhalter auf der Seite statt einer Zahl.
    # Kennzahlen als Gruppen statt als flache Reihe. Ersetzt Liste und
    # Ausgabeschleife der erzeugten Seite in einem Stueck; wiederholbar, weil
    # der eingesetzte Block seine eigenen Marken traegt.
    if "/* kennzahl-gruppen */" in s:
        s = re.sub(r"  /\* kennzahl-gruppen \*/.*?  /\* ende kennzahl-gruppen \*/\n",
                   lambda _: GRUPPEN_NEU, s, count=1, flags=re.S)
        schritte.append("Kennzahl-Gruppen ersetzt")
    elif GRUPPEN_ALT in s:
        s = s.replace(GRUPPEN_ALT, GRUPPEN_NEU, 1)
        schritte.append("Kennzahl-Gruppen eingefuegt")
    else:
        sys.exit("Kennzahlliste nicht gefunden - die erzeugte Seite hat sich geaendert.")

    if RAHMEN_ALT in s:
        s = s.replace(RAHMEN_ALT, RAHMEN_NEU, 1)
        schritte.append("Rahmen umgestellt")

    if CSS_MARKE not in s:
        s = s.replace(".kz{background:var(--flaeche);padding:12px 13px}",
                      ".kz{background:var(--flaeche);padding:12px 13px}" + CSS, 1)
        schritte.append("Gruppen-CSS eingefuegt")

    # Der Rechenweg wird bei jedem Lauf ersetzt, nicht nur beim ersten - sonst
    # kommt eine Korrektur an der Darstellung nie auf der Seite an. Deshalb
    # steht er zwischen zwei Marken.
    block_auf, block_zu = "  /* wert-rechenweg */\n", "  /* ende wert-rechenweg */\n"
    neu = block_auf + ERKL + block_zu
    if block_auf in s:
        s = re.sub(re.escape(block_auf) + ".*?" + re.escape(block_zu),
                   lambda _: neu, s, count=1, flags=re.S)
        schritte.append("Rechenweg ersetzt")
    else:
        # In die *aktive* Erklaerung, also die letzte im Text definierte.
        stelle = s.rfind("  else return null;")
        if stelle < 0:
            sys.exit("Erklaerungskette nicht gefunden.")
        s = s[:stelle] + neu + s[stelle:]
        schritte.append("Rechenweg eingefuegt")

    # Texte: immer neu schreiben, damit Formulierungsaenderungen ankommen.
    m = re.search(r'(<script[^>]*id="texte"[^>]*>)(.*?)(</script>)', s, re.S)
    TX = json.loads(m.group(2))
    TX["t"].update(TEXTE)
    s = s[:m.start(2)] + json.dumps(TX, ensure_ascii=False, separators=(",", ":")) + s[m.end(2):]
    schritte.append("Texte aktualisiert (%d Schluessel)" % len(TEXTE))

    print("Innerer Wert fuer %d von %d Firmen, %d ohne Zahl."
          % (mit, len(daten), len(daten) - mit))
    for x in schritte:
        print("   " + x)
    if pruefen:
        print("\n--pruefen: nichts geschrieben.")
        return
    open(pfad, "w", encoding="utf-8", newline="").write(s)
    print("\n-> %s" % pfad)


if __name__ == "__main__":
    eintragen("--pruefen" in sys.argv)
