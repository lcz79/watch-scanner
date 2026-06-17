"""
Script one-shot: genera watches.json con catalogo completo.
Eseguire con: python3 build_catalog.py
Output: watches.json nella stessa cartella.
"""
import json, pathlib

def w(id_, brand, model, ref, year_range, movement, case_size, tags, price, image_url=""):
    return {
        "id": id_,
        "brand": brand,
        "model": model,
        "reference": ref,
        "canonical_name": f"{brand} {model} {ref}",
        "year_range": year_range,
        "movement": movement,
        "case_size": case_size,
        "image_url": image_url,
        "tags": tags,
        "avg_price_eur": price,
    }

ROLEX_IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Rolex_Submariner.jpg/400px-Rolex_Submariner.jpg"

catalog = [

    # ══════════════════════════════════════════════════════════════════
    # ROLEX — SUBMARINER (no date)
    # ══════════════════════════════════════════════════════════════════
    w("rolex-sub-6204","Rolex","Submariner","6204","1953–1955","Cal. A296","37mm",["vintage","diving","no-date"],85000),
    w("rolex-sub-6205","Rolex","Submariner","6205","1954–1955","Cal. A260","37mm",["vintage","diving","no-date"],75000),
    w("rolex-sub-6536","Rolex","Submariner","6536","1955–1959","Cal. 1030","37mm",["vintage","diving","no-date"],42000),
    w("rolex-sub-6538","Rolex","Submariner","6538","1954–1959","Cal. 1030","38mm",["vintage","diving","big-crown"],95000),
    w("rolex-sub-5508","Rolex","Submariner","5508","1958–1962","Cal. 1530","38mm",["vintage","diving","no-date"],52000),
    w("rolex-sub-5512","Rolex","Submariner","5512","1959–1980","Cal. 1560/1570","40mm",["vintage","diving","no-date"],38000),
    w("rolex-sub-5513","Rolex","Submariner","5513","1962–1989","Cal. 1520/1530","40mm",["vintage","diving","no-date"],22000),
    w("rolex-sub-14060","Rolex","Submariner","14060","1990–1999","Cal. 3000","40mm",["diving","no-date","steel"],7500),
    w("rolex-sub-14060m","Rolex","Submariner","14060M","2000–2011","Cal. 3130","40mm",["diving","no-date","steel"],8500),
    w("rolex-sub-114060","Rolex","Submariner","114060","2012–2020","Cal. 3130","40mm",["diving","no-date","steel"],8800),
    w("rolex-sub-124060","Rolex","Submariner","124060","2020–present","Cal. 3230","41mm",["diving","no-date","steel"],9500),

    # ROLEX — SUBMARINER DATE
    w("rolex-sub-1680","Rolex","Submariner","1680","1969–1979","Cal. 1575","40mm",["vintage","diving","date"],12000),
    w("rolex-sub-16800","Rolex","Submariner","16800","1979–1984","Cal. 3035","40mm",["vintage","diving","date"],9500),
    w("rolex-sub-168000","Rolex","Submariner","168000","1984–1988","Cal. 3035","40mm",["vintage","diving","date"],9000),
    w("rolex-sub-16610","Rolex","Submariner","16610","1988–2009","Cal. 3135","40mm",["diving","date","steel"],9000),
    w("rolex-sub-16610lv","Rolex","Submariner","16610LV","2003–2010","Cal. 3135","40mm",["diving","date","kermit","green"],18000),
    w("rolex-sub-116610ln","Rolex","Submariner","116610LN","2010–2020","Cal. 3135","40mm",["diving","date","steel","ceramic"],11500,ROLEX_IMG),
    w("rolex-sub-116610lv","Rolex","Submariner","116610LV","2010–2020","Cal. 3135","40mm",["diving","date","hulk","green"],17000),
    w("rolex-sub-126610ln","Rolex","Submariner","126610LN","2020–present","Cal. 3235","41mm",["diving","date","steel","ceramic"],12000),
    w("rolex-sub-126610lv","Rolex","Submariner","126610LV","2020–present","Cal. 3235","41mm",["diving","date","starbucks","green"],14500),

    # ROLEX — GMT-MASTER / GMT-MASTER II
    w("rolex-gmt-6542","Rolex","GMT-Master","6542","1954–1959","Cal. 1035","38mm",["vintage","gmt","bakelite"],38000),
    w("rolex-gmt-1675","Rolex","GMT-Master","1675","1959–1980","Cal. 1565/1575","40mm",["vintage","gmt","pepsi"],15000),
    w("rolex-gmt-16750","Rolex","GMT-Master","16750","1980–1988","Cal. 3075","40mm",["vintage","gmt"],8500),
    w("rolex-gmt-16760","Rolex","GMT-Master","16760","1983–1988","Cal. 3085","40mm",["vintage","gmt","fat-lady","coke"],18000),
    w("rolex-gmt-16700","Rolex","GMT-Master","16700","1988–1999","Cal. 3175","40mm",["gmt","pepsi"],8000),
    w("rolex-gmt-16710","Rolex","GMT-Master II","16710","1989–2007","Cal. 3185","40mm",["gmt","steel"],6500),
    w("rolex-gmt-16710ln","Rolex","GMT-Master II","16710LN","2001–2007","Cal. 3185","40mm",["gmt","all-black"],8500),
    w("rolex-gmt-116710ln","Rolex","GMT-Master II","116710LN","2007–2019","Cal. 3186","40mm",["gmt","batman","ceramic"],11000),
    w("rolex-gmt-116710blnr","Rolex","GMT-Master II","116710BLNR","2013–2019","Cal. 3186","40mm",["gmt","batman","blue-black"],12500),
    w("rolex-gmt-116718ln","Rolex","GMT-Master II","116718LN","2005–2019","Cal. 3186","40mm",["gmt","yellow-gold"],25000),
    w("rolex-gmt-116713ln","Rolex","GMT-Master II","116713LN","2005–2019","Cal. 3186","40mm",["gmt","rolesor"],14000),
    w("rolex-gmt-126710blnr","Rolex","GMT-Master II","126710BLNR","2019–present","Cal. 3285","40mm",["gmt","batman","oystersteel"],13000),
    w("rolex-gmt-126710blro","Rolex","GMT-Master II","126710BLRO","2019–present","Cal. 3285","40mm",["gmt","pepsi","oystersteel"],14000),
    w("rolex-gmt-126711chnr","Rolex","GMT-Master II","126711CHNR","2019–present","Cal. 3285","40mm",["gmt","root-beer","rolesor"],18500),
    w("rolex-gmt-126715chnr","Rolex","GMT-Master II","126715CHNR","2019–present","Cal. 3285","40mm",["gmt","root-beer","everose"],30000),
    w("rolex-gmt-126719blro","Rolex","GMT-Master II","126719BLRO","2019–present","Cal. 3285","40mm",["gmt","pepsi","white-gold"],48000),

    # ROLEX — DAYTONA
    w("rolex-daytona-6239","Rolex","Daytona","6239","1963–1969","Cal. Valjoux 72","36mm",["vintage","chronograph","daytona"],65000),
    w("rolex-daytona-6240","Rolex","Daytona","6240","1965–1969","Cal. Valjoux 72","36mm",["vintage","chronograph","sotto"],45000),
    w("rolex-daytona-6241","Rolex","Daytona","6241","1965–1969","Cal. Valjoux 72","36mm",["vintage","chronograph","daytona"],55000),
    w("rolex-daytona-6262","Rolex","Daytona","6262","1970–1971","Cal. Valjoux 727","36mm",["vintage","chronograph"],55000),
    w("rolex-daytona-6263","Rolex","Daytona","6263","1971–1988","Cal. Valjoux 727","36mm",["vintage","chronograph","daytona"],45000),
    w("rolex-daytona-6265","Rolex","Daytona","6265","1971–1988","Cal. Valjoux 727","36mm",["vintage","chronograph","daytona"],48000),
    w("rolex-daytona-6269","Rolex","Daytona","6269","1978–1988","Cal. Valjoux 727","36mm",["vintage","chronograph","gold"],75000),
    w("rolex-daytona-16516","Rolex","Daytona","16516","1988–2000","Cal. 4030 Zenith","40mm",["chronograph","platinum"],65000),
    w("rolex-daytona-16518","Rolex","Daytona","16518","1988–2000","Cal. 4030 Zenith","40mm",["chronograph","yellow-gold"],28000),
    w("rolex-daytona-16519","Rolex","Daytona","16519","1988–2000","Cal. 4030 Zenith","40mm",["chronograph","white-gold"],32000),
    w("rolex-daytona-16520","Rolex","Daytona","16520","1988–2000","Cal. 4030 Zenith","40mm",["chronograph","steel","el-primero"],28000),
    w("rolex-daytona-116520","Rolex","Daytona","116520","2000–2016","Cal. 4130","40mm",["chronograph","steel","ceramic-bezel"],32000),
    w("rolex-daytona-116523","Rolex","Daytona","116523","2000–2016","Cal. 4130","40mm",["chronograph","rolesor"],28000),
    w("rolex-daytona-116503","Rolex","Daytona","116503","2000–2016","Cal. 4130","40mm",["chronograph","rolesor","yellow"],25000),
    w("rolex-daytona-116500ln","Rolex","Daytona","116500LN","2016–2023","Cal. 4130","40mm",["chronograph","steel","ceramic"],30000),
    w("rolex-daytona-116518ln","Rolex","Daytona","116518LN","2016–2023","Cal. 4130","40mm",["chronograph","yellow-gold","black"],35000),
    w("rolex-daytona-116515ln","Rolex","Daytona","116515LN","2016–2023","Cal. 4130","40mm",["chronograph","everose"],35000),
    w("rolex-daytona-126500ln","Rolex","Daytona","126500LN","2023–present","Cal. 4131","40mm",["chronograph","steel","ceramic"],34000),
    w("rolex-daytona-126519ln","Rolex","Daytona","126519LN","2023–present","Cal. 4131","40mm",["chronograph","white-gold"],55000),
    w("rolex-daytona-126529ln","Rolex","Daytona","126529LN","2023–present","Cal. 4131","40mm",["chronograph","yellow-gold"],52000),
    w("rolex-daytona-126506","Rolex","Daytona","126506","2023–present","Cal. 4131","40mm",["chronograph","platinum"],78000),

    # ROLEX — DATEJUST 36
    w("rolex-dj-1601","Rolex","Datejust","1601","1960–1988","Cal. 1570","36mm",["classic","date","vintage"],5500),
    w("rolex-dj-1603","Rolex","Datejust","1603","1960–1988","Cal. 1570","36mm",["classic","date","vintage"],5000),
    w("rolex-dj-16000","Rolex","Datejust","16000","1977–1987","Cal. 3035","36mm",["classic","date","steel"],5000),
    w("rolex-dj-16013","Rolex","Datejust","16013","1978–1988","Cal. 3035","36mm",["classic","date","rolesor"],5500),
    w("rolex-dj-16220","Rolex","Datejust","16220","1988–2000","Cal. 3135","36mm",["classic","date","steel"],5000),
    w("rolex-dj-16233","Rolex","Datejust","16233","1988–2001","Cal. 3135","36mm",["classic","date","rolesor"],5500),
    w("rolex-dj-16234","Rolex","Datejust","16234","1988–2001","Cal. 3135","36mm",["classic","date","steel","white-gold-bezel"],6000),
    w("rolex-dj-116200","Rolex","Datejust","116200","2000–2016","Cal. 3135","36mm",["classic","date","steel"],5500),
    w("rolex-dj-116233","Rolex","Datejust","116233","2000–2016","Cal. 3135","36mm",["classic","date","rolesor"],6000),
    w("rolex-dj-116234","Rolex","Datejust","116234","2000–2016","Cal. 3135","36mm",["classic","date","diamond-bezel"],7000),
    w("rolex-dj-116203","Rolex","Datejust","116203","2000–2016","Cal. 3135","36mm",["classic","date","rolesor","yellow"],5800),
    w("rolex-dj-126200","Rolex","Datejust","126200","2016–present","Cal. 3235","36mm",["classic","date","steel"],6500),
    w("rolex-dj-126233","Rolex","Datejust","126233","2016–present","Cal. 3235","36mm",["classic","date","rolesor"],7200),
    w("rolex-dj-126234","Rolex","Datejust","126234","2016–present","Cal. 3235","36mm",["classic","date","diamond-bezel"],8500),

    # ROLEX — DATEJUST 41
    w("rolex-dj41-116300","Rolex","Datejust 41","116300","2009–2016","Cal. 3136","41mm",["classic","date","steel"],6500),
    w("rolex-dj41-126300","Rolex","Datejust 41","126300","2016–present","Cal. 3235","41mm",["classic","date","steel"],7000),
    w("rolex-dj41-126301","Rolex","Datejust 41","126301","2016–present","Cal. 3235","41mm",["classic","date","rolesor"],8200),
    w("rolex-dj41-126303","Rolex","Datejust 41","126303","2016–present","Cal. 3235","41mm",["classic","date","rolesor","yellow"],8000),
    w("rolex-dj41-126334","Rolex","Datejust 41","126334","2016–present","Cal. 3235","41mm",["classic","date","steel","white-gold-bezel"],9000),
    w("rolex-dj41-126333","Rolex","Datejust 41","126333","2016–present","Cal. 3235","41mm",["classic","date","rolesor"],9000),

    # ROLEX — DAY-DATE 36
    w("rolex-dd-1803","Rolex","Day-Date","1803","1956–1977","Cal. 1555","36mm",["luxury","day-date","vintage","gold"],18000),
    w("rolex-dd-1807","Rolex","Day-Date","1807","1956–1977","Cal. 1555","36mm",["luxury","day-date","vintage","platinum"],28000),
    w("rolex-dd-18038","Rolex","Day-Date","18038","1978–1990","Cal. 3055","36mm",["luxury","day-date","yellow-gold"],18000),
    w("rolex-dd-18039","Rolex","Day-Date","18039","1978–1990","Cal. 3055","36mm",["luxury","day-date","white-gold"],22000),
    w("rolex-dd-18048","Rolex","Day-Date","18048","1978–1990","Cal. 3055","36mm",["luxury","day-date","platinum"],30000),
    w("rolex-dd-118238","Rolex","Day-Date","118238","1990–2015","Cal. 3155","36mm",["luxury","day-date","yellow-gold"],18000),
    w("rolex-dd-118208","Rolex","Day-Date","118208","1990–2015","Cal. 3155","36mm",["luxury","day-date","white-gold"],22000),
    w("rolex-dd-118235","Rolex","Day-Date","118235","1990–2015","Cal. 3155","36mm",["luxury","day-date","everose"],22000),
    w("rolex-dd-228238","Rolex","Day-Date 40","228238","2015–present","Cal. 3255","40mm",["luxury","day-date","yellow-gold"],32000),
    w("rolex-dd-228206","Rolex","Day-Date 40","228206","2015–present","Cal. 3255","40mm",["luxury","day-date","platinum"],55000),
    w("rolex-dd-228235","Rolex","Day-Date 40","228235","2015–present","Cal. 3255","40mm",["luxury","day-date","everose"],32000),
    w("rolex-dd-228239","Rolex","Day-Date 40","228239","2015–present","Cal. 3255","40mm",["luxury","day-date","white-gold"],35000),

    # ROLEX — EXPLORER
    w("rolex-exp-6298","Rolex","Explorer","6298","1953–1959","Cal. A296","36mm",["vintage","explorer"],22000),
    w("rolex-exp-1016","Rolex","Explorer","1016","1959–1989","Cal. 1560/1570","36mm",["vintage","explorer","classic"],18000),
    w("rolex-exp-14270","Rolex","Explorer","14270","1990–2001","Cal. 3000","36mm",["explorer","steel"],7500),
    w("rolex-exp-114270","Rolex","Explorer","114270","2001–2010","Cal. 3130","36mm",["explorer","steel"],7800),
    w("rolex-exp-214270","Rolex","Explorer","214270","2010–2021","Cal. 3132","39mm",["explorer","steel"],8500),
    w("rolex-exp-124270","Rolex","Explorer","124270","2021–present","Cal. 3230","36mm",["explorer","steel"],7500),

    # ROLEX — EXPLORER II
    w("rolex-exp2-1655","Rolex","Explorer II","1655","1971–1985","Cal. 1575","40mm",["vintage","explorer-2","orange-hand"],22000),
    w("rolex-exp2-16550","Rolex","Explorer II","16550","1985–1988","Cal. 3085","40mm",["vintage","explorer-2"],14000),
    w("rolex-exp2-16570","Rolex","Explorer II","16570","1989–2011","Cal. 3185","40mm",["explorer-2","steel"],7500),
    w("rolex-exp2-216570","Rolex","Explorer II","216570","2011–2021","Cal. 3187","42mm",["explorer-2","steel"],9000),
    w("rolex-exp2-226570","Rolex","Explorer II","226570","2021–present","Cal. 3285","42mm",["explorer-2","steel"],9800),

    # ROLEX — MILGAUSS
    w("rolex-mg-6541","Rolex","Milgauss","6541","1956–1960","Cal. 1080","38mm",["vintage","antimagnetic","milgauss"],30000),
    w("rolex-mg-1019","Rolex","Milgauss","1019","1960–1988","Cal. 1580","38mm",["vintage","antimagnetic","milgauss"],18000),
    w("rolex-mg-116400","Rolex","Milgauss","116400","2007–present","Cal. 3131","40mm",["antimagnetic","milgauss","steel"],9000),
    w("rolex-mg-116400gv","Rolex","Milgauss","116400GV","2007–present","Cal. 3131","40mm",["antimagnetic","milgauss","green-glass"],10500),

    # ROLEX — SEA-DWELLER
    w("rolex-sd-1665","Rolex","Sea-Dweller","1665","1967–1978","Cal. 1575","40mm",["vintage","diving","sea-dweller"],28000),
    w("rolex-sd-16660","Rolex","Sea-Dweller","16660","1978–1988","Cal. 3035","40mm",["vintage","diving","triple-six"],18000),
    w("rolex-sd-16600","Rolex","Sea-Dweller","16600","1988–2008","Cal. 3135","40mm",["diving","sea-dweller","steel"],10500),
    w("rolex-sd-116600","Rolex","Sea-Dweller","116600","2008–2017","Cal. 3135","40mm",["diving","sea-dweller","steel"],11000),
    w("rolex-sd-126600","Rolex","Sea-Dweller","126600","2017–present","Cal. 3235","43mm",["diving","sea-dweller","steel"],13000),

    # ROLEX — DEEPSEA
    w("rolex-ds-116660","Rolex","Deepsea","116660","2008–2018","Cal. 3135","44mm",["diving","deepsea","steel"],14500),
    w("rolex-ds-126660","Rolex","Deepsea","126660","2018–present","Cal. 3235","44mm",["diving","deepsea","steel"],15500),
    w("rolex-ds-136660","Rolex","Deepsea","136660","2023–present","Cal. 3235","50mm",["diving","deepsea","d-blue"],18000),

    # ROLEX — AIR-KING
    w("rolex-ak-5500","Rolex","Air-King","5500","1957–1989","Cal. 1520","34mm",["vintage","air-king"],5500),
    w("rolex-ak-14000","Rolex","Air-King","14000","1990–2002","Cal. 3000","34mm",["air-king","steel"],4500),
    w("rolex-ak-14010","Rolex","Air-King","14010","2002–2007","Cal. 3000","34mm",["air-king","steel"],4500),
    w("rolex-ak-116900","Rolex","Air-King","116900","2016–2022","Cal. 3131","40mm",["air-king","steel"],6200),
    w("rolex-ak-126900","Rolex","Air-King","126900","2022–present","Cal. 3230","40mm",["air-king","steel"],7200),

    # ROLEX — YACHT-MASTER
    w("rolex-ym-16622","Rolex","Yacht-Master","16622","1992–2012","Cal. 3135","40mm",["yacht-master","steel","platinum"],10000),
    w("rolex-ym-16628","Rolex","Yacht-Master","16628","1992–2012","Cal. 3135","40mm",["yacht-master","yellow-gold"],18000),
    w("rolex-ym-116621","Rolex","Yacht-Master","116621","2012–2022","Cal. 3135","40mm",["yacht-master","rolesor","everose"],14000),
    w("rolex-ym-116622","Rolex","Yacht-Master","116622","2012–2022","Cal. 3135","40mm",["yacht-master","steel","platinum"],10500),
    w("rolex-ym-116655","Rolex","Yacht-Master","116655","2015–2022","Cal. 3135","40mm",["yacht-master","everose","rubber"],22000),
    w("rolex-ym-226621","Rolex","Yacht-Master","226621","2022–present","Cal. 3235","40mm",["yacht-master","rolesor","everose"],16000),
    w("rolex-ym-226622","Rolex","Yacht-Master","226622","2022–present","Cal. 3235","40mm",["yacht-master","oystersteel"],11000),
    w("rolex-ym-268621","Rolex","Yacht-Master 37","268621","2019–present","Cal. 2236","37mm",["yacht-master","rolesor","ladies"],13000),

    # ROLEX — YACHT-MASTER II
    w("rolex-ym2-116681","Rolex","Yacht-Master II","116681","2007–present","Cal. 4161","44mm",["yacht-master-2","rolesor","regatta"],16000),
    w("rolex-ym2-116689","Rolex","Yacht-Master II","116689","2007–present","Cal. 4161","44mm",["yacht-master-2","yellow-gold","regatta"],35000),
    w("rolex-ym2-226681","Rolex","Yacht-Master II","226681","2019–present","Cal. 4161","44mm",["yacht-master-2","rolesor"],17000),

    # ROLEX — OYSTER PERPETUAL
    w("rolex-op-114200","Rolex","Oyster Perpetual","114200","2000–2020","Cal. 3130","34mm",["oyster","sport-bracelet","steel"],5500),
    w("rolex-op-114300","Rolex","Oyster Perpetual","114300","2000–2020","Cal. 3132","39mm",["oyster","sport-bracelet","steel"],5800),
    w("rolex-op-116000","Rolex","Oyster Perpetual","116000","2011–2020","Cal. 3130","36mm",["oyster","sport-bracelet","steel"],6000),
    w("rolex-op-124200","Rolex","Oyster Perpetual","124200","2020–present","Cal. 3230","34mm",["oyster","steel","candy-dial"],5500),
    w("rolex-op-124300","Rolex","Oyster Perpetual","124300","2020–present","Cal. 3230","41mm",["oyster","steel","candy-dial"],6200),
    w("rolex-op-276200","Rolex","Oyster Perpetual 28","276200","2022–present","Cal. 2232","28mm",["oyster","ladies","steel"],5000),

    # ROLEX — SKY-DWELLER
    w("rolex-sky-326934","Rolex","Sky-Dweller","326934","2012–present","Cal. 9001","42mm",["sky-dweller","steel","annual-calendar"],14000),
    w("rolex-sky-326938","Rolex","Sky-Dweller","326938","2012–present","Cal. 9001","42mm",["sky-dweller","yellow-gold"],28000),
    w("rolex-sky-326935","Rolex","Sky-Dweller","326935","2012–present","Cal. 9001","42mm",["sky-dweller","rolesor"],19000),
    w("rolex-sky-336934","Rolex","Sky-Dweller","336934","2022–present","Cal. 9001","42mm",["sky-dweller","steel","oystersteel"],15500),
    w("rolex-sky-336935","Rolex","Sky-Dweller","336935","2022–present","Cal. 9001","42mm",["sky-dweller","rolesor"],21000),

    # ROLEX — CELLINI
    w("rolex-cell-50519","Rolex","Cellini Time","50519","2014–present","Cal. 3132","39mm",["dress","cellini","white-gold"],18000),
    w("rolex-cell-50515","Rolex","Cellini Time","50515","2014–present","Cal. 3132","39mm",["dress","cellini","yellow-gold"],15000),
    w("rolex-cell-50535","Rolex","Cellini Date","50535","2015–present","Cal. 3165","39mm",["dress","cellini","date","white-gold"],19000),
    w("rolex-cell-50525","Rolex","Cellini Dual Time","50525","2014–present","Cal. 3180","39mm",["dress","cellini","dual-time","white-gold"],22000),

    # ══════════════════════════════════════════════════════════════════
    # OMEGA — SPEEDMASTER
    # ══════════════════════════════════════════════════════════════════
    w("omega-sp-2915","Omega","Speedmaster","CK 2915","1957–1959","Cal. 321","38.6mm",["vintage","chronograph","speedmaster"],95000),
    w("omega-sp-2998","Omega","Speedmaster","ST 105.002","1960–1963","Cal. 321","38.6mm",["vintage","chronograph","speedmaster"],35000),
    w("omega-sp-105003","Omega","Speedmaster","ST 105.003","1963–1969","Cal. 321","39mm",["vintage","chronograph","speedmaster","moon"],40000),
    w("omega-sp-105012","Omega","Speedmaster","ST 105.012","1965–1970","Cal. 321","39mm",["vintage","chronograph","speedmaster"],30000),
    w("omega-sp-145012","Omega","Speedmaster","ST 145.012","1968–1972","Cal. 861","42mm",["vintage","chronograph","moonwatch"],14000),
    w("omega-sp-145022","Omega","Speedmaster","ST 145.022","1969–1988","Cal. 861","42mm",["vintage","chronograph","moonwatch","apollo"],12000),
    w("omega-sp-35905","Omega","Speedmaster","3590.50","1994–2007","Cal. 1863","42mm",["chronograph","moonwatch","steel"],5500),
    w("omega-sp-31130425001005","Omega","Speedmaster Moonwatch","310.30.42.50.01.005","2021–present","Cal. 3861","42mm",["chronograph","moonwatch","co-axial","master"],6500),
    w("omega-sp-31130425001001","Omega","Speedmaster Moonwatch","310.30.42.50.01.001","2021–present","Cal. 3861","42mm",["chronograph","moonwatch","hesalite"],6000),
    w("omega-sp-32190422001001","Omega","Speedmaster '57","321.90.42.50.01.001","2019–present","Cal. 321","38.6mm",["chronograph","57-heritage","cal-321"],10000),
    w("omega-sp-31030425001005","Omega","Speedmaster Moonwatch","310.30.42.50.02.001","2021–present","Cal. 3861","42mm",["chronograph","moonwatch","dark-sapphire"],10000),
    w("omega-sp-snoopy","Omega","Speedmaster Snoopy","310.32.42.50.02.001","2022–present","Cal. 3861","42mm",["chronograph","moonwatch","snoopy","limited"],12000),
    w("omega-sp-alaska","Omega","Speedmaster Alaska Project","311.32.42.30.04.001","2008–2019","Cal. 3861","42mm",["chronograph","moonwatch","alaska","limited"],8500),

    # OMEGA — SEAMASTER DIVER 300M
    w("omega-sm-253180","Omega","Seamaster Diver 300M","2531.80","1993–2005","Cal. 1120","41mm",["diving","seamaster","steel","bond"],2800),
    w("omega-sm-225480","Omega","Seamaster Diver 300M","2254.80","2005–2007","Cal. 2500","41mm",["diving","seamaster","co-axial"],3200),
    w("omega-sm-21030422003001","Omega","Seamaster Diver 300M","210.30.42.20.03.001","2018–present","Cal. 8800","42mm",["diving","seamaster","co-axial","master"],5500),
    w("omega-sm-21030444210001","Omega","Seamaster Diver 300M","210.30.44.51.03.001","2018–present","Cal. 8806","44mm",["diving","seamaster","300m-titanium"],6000),
    w("omega-sm-22013412103001","Omega","Seamaster Diver 300M","220.13.41.21.03.001","2022–present","Cal. 8806","41mm",["diving","seamaster","nato"],5800),

    # OMEGA — SEAMASTER PLANET OCEAN
    w("omega-po-232304222101001","Omega","Planet Ocean 600M","232.30.42.21.01.001","2011–2020","Cal. 8500","42mm",["diving","planet-ocean","co-axial"],5000),
    w("omega-po-215304422101001","Omega","Planet Ocean 600M","215.30.44.21.01.001","2020–present","Cal. 8900","43.5mm",["diving","planet-ocean","master","titanium"],6500),
    w("omega-po-215924622106001","Omega","Planet Ocean Ultra Deep","215.92.46.22.01.001","2019–present","Cal. 8912","46mm",["diving","planet-ocean","ultra-deep","titanium"],8500),
    w("omega-po-232924622104001","Omega","Planet Ocean Big Size","232.92.46.21.04.001","2014–2019","Cal. 8507","46mm",["diving","planet-ocean","titanium"],5500),

    # OMEGA — SEAMASTER AQUA TERRA
    w("omega-at-231103921031001","Omega","Aqua Terra 150M","231.10.39.21.03.001","2007–2019","Cal. 8500","39mm",["aqua-terra","co-axial","steel"],5000),
    w("omega-at-220124122102001","Omega","Aqua Terra 150M","220.12.41.21.02.001","2022–present","Cal. 8900","41mm",["aqua-terra","master","steel"],5500),
    w("omega-at-231104221206001","Omega","Aqua Terra 150M","231.10.42.21.06.001","2017–2022","Cal. 8500","41.5mm",["aqua-terra","co-axial","steel"],5000),

    # OMEGA — SEAMASTER 300 HERITAGE
    w("omega-sm300-234103941211001","Omega","Seamaster 300","234.10.39.20.01.001","2014–present","Cal. 8806","39mm",["seamaster-300","vintage","bronze"],4500),
    w("omega-sm300-233324121210001","Omega","Seamaster 300M","233.32.41.21.01.001","2014–present","Cal. 8400","41mm",["seamaster-300","master","steel"],5000),

    # OMEGA — CONSTELLATION
    w("omega-co-2523","Omega","Constellation","123.10.38.21.02.001","2009–2018","Cal. 8520","38mm",["constellation","co-axial","steel"],4500),
    w("omega-co-131104122065001","Omega","Constellation Manhattan","131.10.41.21.22.001","2018–present","Cal. 8800","41mm",["constellation","manhattan","master"],5500),
    w("omega-co-131232920655001","Omega","Constellation","131.23.29.20.13.001","2018–present","Cal. 8700","29mm",["constellation","ladies","master"],4000),
    w("omega-co-131103622055001","Omega","Constellation","131.10.36.20.05.001","2018–present","Cal. 8700","36mm",["constellation","master","ladies"],4500),

    # OMEGA — DE VILLE
    w("omega-dv-424134002102001","Omega","De Ville Trésor","424.13.40.21.02.001","2014–present","Cal. 8511","40mm",["dress","de-ville","tresor","manual"],5000),
    w("omega-dv-431534102211001","Omega","De Ville Prestige","431.53.41.21.01.001","2013–present","Cal. 8511","41mm",["dress","de-ville","prestige"],4500),

    # OMEGA — SPEEDMASTER RACING / REDUCED
    w("omega-sp-3539","Omega","Speedmaster Reduced","3539.50","1999–2015","Cal. 3220","39mm",["chronograph","speedmaster","automatic"],2800),

    # ══════════════════════════════════════════════════════════════════
    # PATEK PHILIPPE
    # ══════════════════════════════════════════════════════════════════

    # NAUTILUS
    w("pp-naut-3700","Patek Philippe","Nautilus","3700/1A","1976–1990","Cal. 28-255","42mm",["nautilus","vintage","steel","jumbo"],85000),
    w("pp-naut-3800","Patek Philippe","Nautilus","3800/1A","1981–2006","Cal. 330 SC","38mm",["nautilus","steel"],30000),
    w("pp-naut-57111a","Patek Philippe","Nautilus","5711/1A-001","2006–2021","Cal. 324 SC","40mm",["nautilus","steel","blue"],120000),
    w("pp-naut-57111a010","Patek Philippe","Nautilus","5711/1A-010","2021","Cal. 324 SC","40mm",["nautilus","steel","tiffany","limited"],400000),
    w("pp-naut-5711r","Patek Philippe","Nautilus","5711/1R-001","2020–2021","Cal. 324 SC","40mm",["nautilus","rose-gold"],95000),
    w("pp-naut-57121a","Patek Philippe","Nautilus","5712/1A-001","2006–present","Cal. 240 PS IRM C LU","40mm",["nautilus","moonphase","power-reserve","steel"],70000),
    w("pp-naut-5726a","Patek Philippe","Nautilus","5726/1A-014","2014–present","Cal. 324 S QA LU 24H","40mm",["nautilus","annual-calendar","steel"],85000),
    w("pp-naut-5726g","Patek Philippe","Nautilus","5726/1G-001","2019–present","Cal. 324 S QA LU 24H","40mm",["nautilus","annual-calendar","white-gold"],120000),
    w("pp-naut-59901a","Patek Philippe","Nautilus","5990/1A-001","2012–present","Cal. CH 28-520 C","40.5mm",["nautilus","chronograph","flyback","steel"],90000),
    w("pp-naut-59801a","Patek Philippe","Nautilus","5980/1A-001","2006–2022","Cal. CH 28-520 C","40.5mm",["nautilus","chronograph","steel"],85000),
    w("pp-naut-57401g","Patek Philippe","Nautilus","5740/1G-001","2018–present","Cal. 240 Q","40mm",["nautilus","perpetual-calendar","white-gold"],160000),
    w("pp-naut-57191g","Patek Philippe","Nautilus","5719/1G-001","2014–present","Cal. 324 SC","35.2mm",["nautilus","ladies","white-gold"],55000),

    # AQUANAUT
    w("pp-aq-5060a","Patek Philippe","Aquanaut","5060A","1997–2007","Cal. 315 SC","36mm",["aquanaut","steel","rubber"],30000),
    w("pp-aq-5065a","Patek Philippe","Aquanaut","5065A","1997–2009","Cal. 315 SC","36mm",["aquanaut","steel","rubber"],28000),
    w("pp-aq-5167a","Patek Philippe","Aquanaut","5167A-001","2011–present","Cal. 324 SC","40mm",["aquanaut","steel","rubber","blue"],50000),
    w("pp-aq-5167r","Patek Philippe","Aquanaut","5167R-001","2011–present","Cal. 324 SC","40mm",["aquanaut","rose-gold","rubber"],65000),
    w("pp-aq-5168g","Patek Philippe","Aquanaut","5168G-001","2019–present","Cal. 324 SC","42.2mm",["aquanaut","white-gold","blue"],85000),
    w("pp-aq-5168g010","Patek Philippe","Aquanaut","5168G-010","2019–present","Cal. 324 SC","42.2mm",["aquanaut","white-gold","khaki"],85000),
    w("pp-aq-5164a","Patek Philippe","Aquanaut","5164A-001","2011–present","Cal. 324 SC FUS 24H","40.8mm",["aquanaut","travel-time","steel"],55000),

    # CALATRAVA
    w("pp-cal-5119g","Patek Philippe","Calatrava","5119G-001","2002–present","Cal. 215 PS","35mm",["calatrava","dress","white-gold"],30000),
    w("pp-cal-5119p","Patek Philippe","Calatrava","5119P-001","2002–present","Cal. 215 PS","35mm",["calatrava","dress","platinum"],38000),
    w("pp-cal-5127g","Patek Philippe","Calatrava","5127G-001","2004–present","Cal. 315 S","37mm",["calatrava","dress","white-gold"],38000),
    w("pp-cal-5196g","Patek Philippe","Calatrava","5196G-001","2005–present","Cal. 215 PS","37mm",["calatrava","dress","white-gold"],28000),
    w("pp-cal-5196p","Patek Philippe","Calatrava","5196P-001","2005–present","Cal. 215 PS","37mm",["calatrava","dress","platinum"],38000),
    w("pp-cal-6006g","Patek Philippe","Calatrava","6006G-001","2018–present","Cal. 26-330 SC FUS","40mm",["calatrava","weekly-calendar","white-gold"],75000),
    w("pp-cal-6119g","Patek Philippe","Calatrava","6119G-010","2019–present","Cal. 30-255 PS","38mm",["calatrava","dress","white-gold"],40000),
    w("pp-cal-5153g","Patek Philippe","Calatrava","5153G-001","2004–present","Cal. 315 SC","38mm",["calatrava","officer","white-gold"],42000),
    w("pp-cal-3939","Patek Philippe","Calatrava","3939","1989–2009","Cal. TO 12-400 AS","36mm",["calatrava","tourbillon","minute-repeater"],850000),

    # GRAND COMPLICATIONS
    w("pp-gc-5270g","Patek Philippe","Perpetual Chronograph","5270G-013","2014–present","Cal. CH 29-535 PS Q","41mm",["grand-complications","perpetual-calendar","chronograph","white-gold"],200000),
    w("pp-gc-5270p","Patek Philippe","Perpetual Chronograph","5270P-001","2011–present","Cal. CH 29-535 PS Q","41mm",["grand-complications","perpetual-calendar","chronograph","platinum"],250000),
    w("pp-gc-5207g","Patek Philippe","Celestial Sky Moon Tourbillon","5207G-001","2012–present","Cal. TO 36 PS QR SV","45.5mm",["grand-complications","tourbillon","minute-repeater"],1500000),
    w("pp-gc-5004p","Patek Philippe","Perpetual Calendar Chronograph","5004P","1994–2010","Cal. CHR 27-70 Q","36mm",["grand-complications","perpetual-calendar","split-second"],300000),
    w("pp-gc-5970g","Patek Philippe","Chronograph","5970G-001","2004–2011","Cal. CHR 27-525 PS","40mm",["complications","chronograph","white-gold"],200000),
    w("pp-gc-5170j","Patek Philippe","Chronograph","5170J-001","2011–present","Cal. CH 29-535 PS","39.4mm",["complications","chronograph","yellow-gold"],100000),
    w("pp-gc-5172g","Patek Philippe","Flyback Chronograph","5172G-001","2019–present","Cal. CH 28-520 HU","41mm",["complications","flyback","chronograph","white-gold"],120000),
    w("pp-gc-5204r","Patek Philippe","Split Second Chronograph","5204R-011","2019–present","Cal. CHR 29-535 PS","40mm",["complications","split-second","chronograph","rose-gold"],350000),

    # ANNUAL CALENDAR
    w("pp-ac-5396g","Patek Philippe","Annual Calendar","5396G-014","2006–present","Cal. 324 S QA LU 24H","38.5mm",["annual-calendar","moonphase","white-gold"],60000),
    w("pp-ac-5396r","Patek Philippe","Annual Calendar","5396R-001","2006–present","Cal. 324 S QA LU 24H","38.5mm",["annual-calendar","moonphase","rose-gold"],55000),
    w("pp-ac-5205g","Patek Philippe","Annual Calendar","5205G-013","2011–present","Cal. 324 S QA LU 24H","40mm",["annual-calendar","moonphase","white-gold"],65000),

    # WORLD TIME
    w("pp-wt-5130p","Patek Philippe","World Time","5130P-001","2006–present","Cal. 240 HU","39.5mm",["world-time","platinum"],110000),
    w("pp-wt-5230g","Patek Philippe","World Time","5230G-010","2016–present","Cal. 240 HU","38.5mm",["world-time","moonphase","white-gold"],120000),
    w("pp-wt-5131r","Patek Philippe","World Time","5131R-001","2012–present","Cal. 240 HU","39.5mm",["world-time","rose-gold","enamel"],130000),

    # ══════════════════════════════════════════════════════════════════
    # AUDEMARS PIGUET
    # ══════════════════════════════════════════════════════════════════

    # ROYAL OAK
    w("ap-ro-5402st","Audemars Piguet","Royal Oak","5402ST","1972–1984","Cal. 2121","39mm",["royal-oak","vintage","jumbo","steel"],120000),
    w("ap-ro-14802st","Audemars Piguet","Royal Oak","14802ST","1986–1992","Cal. 2121","36mm",["royal-oak","vintage","steel"],35000),
    w("ap-ro-15000st","Audemars Piguet","Royal Oak","15000ST","1992–2005","Cal. 2121","33mm",["royal-oak","steel","thin"],15000),
    w("ap-ro-15202st","Audemars Piguet","Royal Oak","15202ST","1992–present","Cal. 2121","39mm",["royal-oak","jumbo","extra-thin","steel"],75000),
    w("ap-ro-15202or","Audemars Piguet","Royal Oak","15202OR","1992–present","Cal. 2121","39mm",["royal-oak","jumbo","extra-thin","rose-gold"],120000),
    w("ap-ro-15202bc","Audemars Piguet","Royal Oak","15202BC","1992–present","Cal. 2121","39mm",["royal-oak","jumbo","extra-thin","white-gold"],140000),
    w("ap-ro-15300st","Audemars Piguet","Royal Oak","15300ST","2005–2012","Cal. 3120","39mm",["royal-oak","date","steel"],18000),
    w("ap-ro-15400st","Audemars Piguet","Royal Oak","15400ST","2012–2020","Cal. 3120","41mm",["royal-oak","date","steel"],22000),
    w("ap-ro-15500st","Audemars Piguet","Royal Oak","15500ST","2020–present","Cal. 4302","41mm",["royal-oak","date","steel"],35000),
    w("ap-ro-15510st","Audemars Piguet","Royal Oak","15510ST","2020–present","Cal. 4302","41mm",["royal-oak","date","slate"],35000),
    w("ap-ro-26331st","Audemars Piguet","Royal Oak Chronograph","26331ST","2012–present","Cal. 2385","41mm",["royal-oak","chronograph","steel"],32000),
    w("ap-ro-26331or","Audemars Piguet","Royal Oak Chronograph","26331OR","2012–present","Cal. 2385","41mm",["royal-oak","chronograph","rose-gold"],65000),

    # ROYAL OAK PERPETUAL CALENDAR
    w("ap-ropc-25820or","Audemars Piguet","Royal Oak Perpetual Calendar","25820OR","2000–2012","Cal. 2120/2802","39mm",["royal-oak","perpetual-calendar","rose-gold"],120000),
    w("ap-ropc-26574st","Audemars Piguet","Royal Oak Perpetual Calendar","26574ST","2019–present","Cal. 5134","41mm",["royal-oak","perpetual-calendar","steel"],120000),
    w("ap-ropc-26574or","Audemars Piguet","Royal Oak Perpetual Calendar","26574OR","2019–present","Cal. 5134","41mm",["royal-oak","perpetual-calendar","rose-gold"],180000),

    # ROYAL OAK OFFSHORE
    w("ap-roo-25721ti","Audemars Piguet","Royal Oak Offshore","25721TI","1993–2004","Cal. 2226/2840","42mm",["royal-oak-offshore","first","titanium"],38000),
    w("ap-roo-26400ro","Audemars Piguet","Royal Oak Offshore","26400RO","2012–2020","Cal. 3126/3840","44mm",["royal-oak-offshore","rose-gold","offshore"],65000),
    w("ap-roo-26470st","Audemars Piguet","Royal Oak Offshore","26470ST","2015–present","Cal. 3126/3840","42mm",["royal-oak-offshore","steel","offshore"],35000),
    w("ap-roo-26480ti","Audemars Piguet","Royal Oak Offshore Chronograph","26480TI","2019–present","Cal. 2385","44mm",["royal-oak-offshore","chronograph","titanium"],45000),
    w("ap-roo-26560ce","Audemars Piguet","Royal Oak Offshore","26560CE","2020–present","Cal. 4401","44mm",["royal-oak-offshore","ceramic","selfwinding"],65000),
    w("ap-roo-26403ce","Audemars Piguet","Royal Oak Offshore","26403CE","2019–present","Cal. 4401","43mm",["royal-oak-offshore","ceramic","flyback"],55000),

    # CODE 11.59
    w("ap-code-15210bc","Audemars Piguet","Code 11.59","15210BC","2019–present","Cal. 4302","41mm",["code-1159","white-gold","dress"],40000),
    w("ap-code-15210or","Audemars Piguet","Code 11.59","15210OR","2019–present","Cal. 4302","41mm",["code-1159","rose-gold"],38000),
    w("ap-code-15210st","Audemars Piguet","Code 11.59","15210ST","2019–present","Cal. 4302","41mm",["code-1159","steel"],22000),
    w("ap-code-26393cr","Audemars Piguet","Code 11.59 Perpetual Calendar Chronograph","26393CR","2019–present","Cal. 2956","41mm",["code-1159","perpetual-calendar","chronograph"],200000),

    # ══════════════════════════════════════════════════════════════════
    # VACHERON CONSTANTIN
    # ══════════════════════════════════════════════════════════════════
    w("vc-os-42050","Vacheron Constantin","Overseas","42050/423A","1996–2004","Cal. 1126/37","37mm",["overseas","vintage","steel"],15000),
    w("vc-os-47040","Vacheron Constantin","Overseas","47040/B01A","2004–2016","Cal. 2500 V/2","42mm",["overseas","steel","automatic"],18000),
    w("vc-os-49150","Vacheron Constantin","Overseas Chronograph","49150/000A","2007–2016","Cal. 1137","42mm",["overseas","chronograph","steel"],28000),
    w("vc-os-4500v","Vacheron Constantin","Overseas","4500V/110A-B483","2016–present","Cal. 5100","41mm",["overseas","steel","blue","interchangeable"],25000),
    w("vc-os-4500v128","Vacheron Constantin","Overseas","4500V/110A-B128","2016–present","Cal. 5100","41mm",["overseas","steel","blue"],25000),
    w("vc-os-5500v","Vacheron Constantin","Overseas","5500V/110A-B148","2016–present","Cal. 5200","41mm",["overseas","steel","dual-time"],28000),
    w("vc-os-7900v","Vacheron Constantin","Overseas Tourbillon","7900V/110A","2016–present","Cal. 2790","42.5mm",["overseas","tourbillon","steel"],185000),
    w("vc-os-5100v","Vacheron Constantin","Overseas Perpetual Calendar","5100V/110B","2018–present","Cal. 3400","43mm",["overseas","perpetual-calendar"],140000),
    w("vc-os-4300v","Vacheron Constantin","Overseas Self-Winding","4300V/120G-B945","2021–present","Cal. 5100","41mm",["overseas","gold","automatic"],45000),

    # TRADITIONNELLE
    w("vc-tr-82172","Vacheron Constantin","Traditionnelle","82172/000R-9382","2011–present","Cal. 2460 SC","38mm",["traditionnelle","dress","rose-gold"],28000),
    w("vc-tr-87172","Vacheron Constantin","Traditionnelle Minute Repeater","87172/000R-9888","2017–present","Cal. 3600","40mm",["traditionnelle","minute-repeater","rose-gold"],650000),

    # PATRIMONY
    w("vc-pat-81180","Vacheron Constantin","Patrimony","81180/000R-9159","2012–present","Cal. 2450 Q6","40mm",["patrimony","ultra-thin","rose-gold"],28000),
    w("vc-pat-85180","Vacheron Constantin","Patrimony","85180/000G-9231","2012–present","Cal. 1400","36mm",["patrimony","ultra-thin","white-gold","ladies"],25000),
    w("vc-pat-43175","Vacheron Constantin","Patrimony Perpetual Calendar","43175/000R-9687","2012–present","Cal. 1120 QP","41mm",["patrimony","perpetual-calendar","rose-gold"],90000),

    # HISTORIQUES
    w("vc-hi-86300","Vacheron Constantin","Historiques American 1921","86300/000R-9153","2009–present","Cal. 4400 AS","40mm",["historiques","driver","rose-gold"],38000),

    # ══════════════════════════════════════════════════════════════════
    # TAG HEUER
    # ══════════════════════════════════════════════════════════════════

    # CARRERA
    w("th-ca-2447","TAG Heuer","Carrera","2447","1963–1968","Cal. Valjoux 92/72","36mm",["vintage","carrera","chronograph"],30000),
    w("th-ca-1153s","TAG Heuer","Carrera","1153S","1970–1972","Cal. 11","36mm",["vintage","carrera","automatic"],18000),
    w("th-ca-cv2010","TAG Heuer","Carrera Calibre 16","CV2010.BA0794","2007–2017","Cal. 16","41mm",["carrera","chronograph","steel"],3500),
    w("th-ca-cv2011","TAG Heuer","Carrera Calibre 16","CV2011.BA0786","2007–2017","Cal. 16","41mm",["carrera","chronograph","black"],3500),
    w("th-ca-car201a","TAG Heuer","Carrera Calibre 1","CAR201A.BA0714","2014–2019","Cal. 1887","43mm",["carrera","chronograph","tourbillon"],7000),
    w("th-ca-cbn2a1a","TAG Heuer","Carrera Calibre Heuer 02","CBN2A1A.BA0643","2019–present","Cal. Heuer 02","44mm",["carrera","chronograph","in-house"],3200),
    w("th-ca-cbs2010","TAG Heuer","Carrera","CBS2010.BA0111","2021–present","Cal. 5","39mm",["carrera","steel","new-gen"],2800),
    w("th-ca-cbg2011","TAG Heuer","Carrera Calibre Heuer 02","CBG2011.BA0658","2019–present","Cal. Heuer 02","44mm",["carrera","chronograph"],3200),

    # MONACO
    w("th-mo-1133g","TAG Heuer","Monaco","1133G","1969–1975","Cal. 11","40mm",["vintage","monaco","square","first"],55000),
    w("th-mo-1533g","TAG Heuer","Monaco","1533G","1971–1975","Cal. 11","40mm",["vintage","monaco","square"],45000),
    w("th-mo-caw2111","TAG Heuer","Monaco","CAW2111.BA0160","2009–2019","Cal. 11","39mm",["monaco","square","chronograph"],5000),
    w("th-mo-caw2111fc","TAG Heuer","Monaco Gulf","CAW2111.FC6183","2009–2019","Cal. 11","39mm",["monaco","gulf","chronograph"],6000),
    w("th-mo-cbl2111","TAG Heuer","Monaco","CBL2111.BA0644","2019–present","Cal. Heuer 02","39mm",["monaco","square","in-house"],5500),
    w("th-mo-cbs2111","TAG Heuer","Monaco Gulf","CBS2111.FC6535","2020–present","Cal. Heuer 02","39mm",["monaco","gulf","limited"],7000),

    # AUTAVIA
    w("th-au-2446","TAG Heuer","Autavia","2446","1962–1969","Cal. Valjoux 92","38mm",["vintage","autavia","panda"],35000),
    w("th-au-cbe2110","TAG Heuer","Autavia","CBE2110.BA0687","2017–present","Cal. Isograph 02","42mm",["autavia","chronograph","isograph"],3200),

    # AQUARACER
    w("th-aq-way2010","TAG Heuer","Aquaracer 300M","WAY2010.BA0927","2014–2020","Cal. 5","41mm",["aquaracer","diving","300m"],1800),
    w("th-aq-wbn2111","TAG Heuer","Aquaracer","WBD2111.BA0928","2021–present","Cal. Heuer 09","43mm",["aquaracer","chronograph"],2500),
    w("th-aq-wak2110","TAG Heuer","Aquaracer Professional 500","WBN2113.BA0639","2021–present","Cal. 5","43mm",["aquaracer","500m","diving"],2200),

    # FORMULA 1
    w("th-f1-waz1110","TAG Heuer","Formula 1","WAZ1110.BA0875","2019–present","Cal. 5","44mm",["formula1","steel","sport"],1200),

    # LINK
    w("th-li-wjf2112","TAG Heuer","Link","WJF2112.BA0572","2012–2018","Cal. 7","41mm",["link","chronograph","steel"],2800),

    # ══════════════════════════════════════════════════════════════════
    # TUDOR
    # ══════════════════════════════════════════════════════════════════

    # BLACK BAY VINTAGE
    w("tudor-bb-7922","Tudor","Black Bay (original Submariner)","7922","1954–1957","Cal. A390","37mm",["vintage","submariner","tudor"],8000),
    w("tudor-bb-7924","Tudor","Submariner Snowflake","7924","1969–1983","Cal. 2483","40mm",["vintage","submariner","snowflake"],12000),
    w("tudor-bb-94010","Tudor","Prince Oysterdate Submariner","94010","1970–1990","Cal. 2824","40mm",["vintage","submariner","tudor"],6000),

    # BLACK BAY MODERN
    w("tudor-bb-79220r","Tudor","Black Bay","M79220R-0001","2012–2016","Cal. MT5612","41mm",["black-bay","red-bezel","steel"],3500),
    w("tudor-bb-79230n","Tudor","Black Bay","M79230N-0001","2014–2020","Cal. MT5612","41mm",["black-bay","black-bezel","steel"],3500),
    w("tudor-bb-79540","Tudor","Black Bay Blue","M79540-0001","2014–2020","Cal. MT5612","41mm",["black-bay","blue-bezel","steel"],3800),
    w("tudor-bb-m79733n","Tudor","Black Bay Pro","M79733N-0001","2022–present","Cal. MT5612","39mm",["black-bay","pro","gmt"],4500),
    w("tudor-bb-m79543","Tudor","Black Bay Steel & Gold","M79543-0001","2017–present","Cal. MT5612","41mm",["black-bay","steel-gold","dual-tone"],5000),

    # BLACK BAY 58
    w("tudor-bb58-m79030n","Tudor","Black Bay 58","M79030N-0001","2018–present","Cal. MT5402","39mm",["black-bay-58","black","vintage"],3400),
    w("tudor-bb58-m79030b","Tudor","Black Bay 58 Navy Blue","M79030B-0001","2018–present","Cal. MT5402","39mm",["black-bay-58","navy-blue"],3400),
    w("tudor-bb58-m79030ub","Tudor","Black Bay 58 Green","M79030UB-0001","2020–present","Cal. MT5402","39mm",["black-bay-58","green"],3800),
    w("tudor-bb58-m79030gz","Tudor","Black Bay 58 Gold","M79030GZ-0001","2021–present","Cal. MT5402","39mm",["black-bay-58","gold","yellow"],8000),
    w("tudor-bb58-m79010sg","Tudor","Black Bay 58 925","M79010SG-0001","2021–present","Cal. MT5402","39mm",["black-bay-58","silver","limited"],5500),

    # BLACK BAY GMT
    w("tudor-bbgmt-m79830rb","Tudor","Black Bay GMT","M79830RB-0001","2018–present","Cal. MT5652","41mm",["black-bay","gmt","red-blue","pepsi"],4000),
    w("tudor-bbgmt-m79830bb","Tudor","Black Bay GMT","M79830BB-0001","2019–present","Cal. MT5652","41mm",["black-bay","gmt","blue"],4000),
    w("tudor-bbgmt-m79843","Tudor","Black Bay GMT S&G","M79843-0001","2021–present","Cal. MT5652","41mm",["black-bay","gmt","steel-gold"],5500),

    # PELAGOS
    w("tudor-pel-m25600tn","Tudor","Pelagos","M25600TN-0001","2012–present","Cal. MT5612","42mm",["pelagos","titanium","blue","diver"],4500),
    w("tudor-pel-m25600tb","Tudor","Pelagos","M25600TB-0001","2012–present","Cal. MT5612","42mm",["pelagos","titanium","black"],4500),
    w("tudor-pel-m25607tb","Tudor","Pelagos FXD","M25607TB-0001","2022–present","Cal. MT5612","42mm",["pelagos","fxd","titanium","nato"],4800),
    w("tudor-pel-m25718tn","Tudor","Pelagos 39","M25718TN-0001","2023–present","Cal. MT5400","39mm",["pelagos","39mm","titanium"],4200),

    # HERITAGE CHRONO
    w("tudor-hc-m70330n","Tudor","Heritage Chrono","M70330N-0001","2010–2023","Cal. ETA 2892+2014","42mm",["heritage","chronograph","vintage"],3500),

    # RANGER
    w("tudor-ran-m79950","Tudor","Ranger","M79950-0001","2021–present","Cal. MT5402","39mm",["ranger","field","steel"],3000),

    # ══════════════════════════════════════════════════════════════════
    # RICHARD MILLE
    # ══════════════════════════════════════════════════════════════════
    w("rm-001","Richard Mille","RM 001 Tourbillon","RM 001","2001–2002","Cal. RM001","38.7×47.75mm",["rm","tourbillon","limited","titanium"],1200000),
    w("rm-004","Richard Mille","RM 004 Tourbillon","RM 004","2003–2010","Cal. RM 004","38.7×47.75mm",["rm","tourbillon","split-second"],900000),
    w("rm-005","Richard Mille","RM 005 Automatic","RM 005","2004–2012","Cal. RMAC1","40.9×49.9mm",["rm","automatic","titanium"],200000),
    w("rm-010","Richard Mille","RM 010 Automatic","RM 010","2006–2014","Cal. RMAC2","39.7×48.2mm",["rm","automatic","titanium"],180000),
    w("rm-011","Richard Mille","RM 011 Annual Calendar Flyback","RM 011","2007–present","Cal. RMAC2","40×50mm",["rm","chronograph","annual-calendar","flyback"],220000),
    w("rm-016","Richard Mille","RM 016 Tourbillon","RM 016","2009–2015","Cal. RM007 TO","44.5×57.5mm",["rm","tourbillon","automatic"],380000),
    w("rm-027","Richard Mille","RM 027 Tourbillon Nadal","RM 027","2010–present","Cal. RM036","44.5×38mm",["rm","tourbillon","nadal","limited"],750000),
    w("rm-035","Richard Mille","RM 035 Americas","RM 035-01","2012–present","Cal. RMAL1","38.2×47.75mm",["rm","automatic","nadal","ceramic"],200000),
    w("rm-035-02","Richard Mille","RM 035-02","RM 035-02","2014–present","Cal. RMAL1","38.2×47.75mm",["rm","automatic","carbon"],180000),
    w("rm-050","Richard Mille","RM 050 Tourbillon Chronograph","RM 050","2009–2012","Cal. RM50","51×44mm",["rm","tourbillon","chronograph","split-second"],1800000),
    w("rm-055","Richard Mille","RM 055 Bubba Watson","RM 055","2012–present","Cal. RMAL1","44.5×38mm",["rm","automatic","white","bubba"],180000),
    w("rm-056","Richard Mille","RM 056 Tourbillon Sapphire","RM 056","2012","Cal. RM056","50.3×42.7mm",["rm","tourbillon","sapphire","ultra-limited"],2000000),
    w("rm-067","Richard Mille","RM 067 Automatic","RM 067-01","2017–present","Cal. RMAC1","45.7×30mm",["rm","automatic","ultra-thin","ladies"],150000),
    w("rm-071","Richard Mille","RM 71-01 Automatic","RM 71-01","2019–present","Cal. RMAL1","50×40mm",["rm","automatic","ladies","flower"],300000),

    # ══════════════════════════════════════════════════════════════════
    # IWC
    # ══════════════════════════════════════════════════════════════════
    w("iwc-pp-iw3777","IWC","Pilot's Watch Mark XVIII","IW327001","2016–present","Cal. 30110","40mm",["pilot","iwc","steel"],4500),
    w("iwc-pp-iw3270","IWC","Pilot's Watch Mark XX","IW328201","2022–present","Cal. 82200","40mm",["pilot","iwc","automatic"],5500),
    w("iwc-pp-bigpilot","IWC","Big Pilot's Watch","IW501001","2004–present","Cal. 5011","46.2mm",["pilot","big-pilot","iwc","steel"],12000),
    w("iwc-pp-iw3777-11","IWC","Pilot's Watch Mark XVIII Le Petit Prince","IW327010","2018–present","Cal. 30110","40mm",["pilot","iwc","blue","le-petit-prince"],5500),
    w("iwc-sp-iw3716","IWC","Spitfire","IW387901","2019–present","Cal. 69380","41mm",["pilot","spitfire","iwc"],5000),
    w("iwc-pd-iw3546","IWC","Portofino Automatic","IW356501","2014–present","Cal. 35111","40mm",["portofino","dress","steel"],4500),
    w("iwc-aq-iw3508","IWC","Aquatimer Automatic","IW329001","2014–present","Cal. 80111","42mm",["aquatimer","diver","iwc","steel"],5000),
    w("iwc-pd2","IWC","Portofino Hand-Wound Eight Days","IW510103","2014–present","Cal. 59210","45mm",["portofino","manual-wind","steel"],8500),
    w("iwc-pp-flieger","IWC","Flieger Pilot Mark XI","IW326501","2012–present","Cal. 30110","36mm",["pilot","mark-xi","vintage"],6500),
    w("iwc-ing-iw3777","IWC","Ingenieur Automatic","IW323902","2023–present","Cal. 32000","40mm",["ingenieur","steel","iwc"],6000),

    # ══════════════════════════════════════════════════════════════════
    # PANERAI
    # ══════════════════════════════════════════════════════════════════
    w("pam-luminor-pam00372","Panerai","Luminor Marina","PAM00372","2009–present","Cal. OP III","44mm",["luminor","marina","steel"],8000),
    w("pam-luminor-pam00005","Panerai","Luminor Marina 1950","PAM00005","2002–present","Cal. OP I","44mm",["luminor","1950","steel"],9000),
    w("pam-luminor-pam01392","Panerai","Luminor Due","PAM01392","2019–present","Cal. P.900","42mm",["luminor","due","steel","thin"],8500),
    w("pam-luminor-pam00024","Panerai","Luminor Submersible","PAM00024","1998–present","Cal. OP III","44mm",["luminor","submersible","diver"],9000),
    w("pam-radiomir-pam00183","Panerai","Radiomir Black Seal","PAM00183","2005–present","Cal. OP III","45mm",["radiomir","black-seal","steel"],7000),
    w("pam-radiomir-pam00514","Panerai","Radiomir 1940","PAM00514","2012–present","Cal. P.3000","45mm",["radiomir","1940","steel"],8000),
    w("pam-luminor-pam00673","Panerai","Luminor Base Logo","PAM00673","2017–present","Cal. P.6000","44mm",["luminor","base","steel"],7500),
    w("pam-luminor-pam01359","Panerai","Luminor Marina eSteel","PAM01359","2021–present","Cal. P.900","44mm",["luminor","eco","sustainable"],8500),

    # ══════════════════════════════════════════════════════════════════
    # BREITLING
    # ══════════════════════════════════════════════════════════════════
    w("br-nav-ab0138","Breitling","Navitimer 01","AB0138","2013–2020","Cal. B01","43mm",["navitimer","chronograph","pilot","steel"],6000),
    w("br-nav-ab012012","Breitling","Navitimer 01","AB012012","2013–2020","Cal. B01","46mm",["navitimer","chronograph","pilot","steel"],6500),
    w("br-nav-ab0139241b1a1","Breitling","Navitimer B01","AB0139241B1A1","2020–present","Cal. B01","43mm",["navitimer","chronograph","pilot","steel"],7000),
    w("br-sup-m10380","Breitling","Superocean Heritage II","M10380","2017–present","Cal. B20","42mm",["superocean","heritage","diver"],4500),
    w("br-sup-ab2030","Breitling","Superocean Automatic 42","AB2030","2021–present","Cal. B20","42mm",["superocean","diver","steel"],4000),
    w("br-chr-cb0142","Breitling","Chronomat","CB0142","2012–2020","Cal. B01","47mm",["chronomat","chronograph","steel"],5500),
    w("br-chr-ab0134","Breitling","Chronomat 44","AB0134","2012–2020","Cal. B01","44mm",["chronomat","chronograph","steel"],5000),
    w("br-chr-ab0134101c1a1","Breitling","Chronomat B01","AB0134101C1A1","2020–present","Cal. B01","44mm",["chronomat","chronograph","steel"],6000),
    w("br-avi-ab0920","Breitling","Avenger Automatic 45","AB0920","2020–present","Cal. B17","45mm",["avenger","pilot","steel"],3800),
    w("br-avi-a13317","Breitling","Avenger II GMT","A13317","2011–2019","Cal. B04","45mm",["avenger","gmt","steel"],4500),
    w("br-avi-a13390","Breitling","Avenger II","A13390","2011–2019","Cal. B13","44mm",["avenger","chronograph","steel"],4000),
    w("br-emer-a12310","Breitling","Emergency","A12310","2000–2013","Cal. B12","43mm",["emergency","pilot","titanium"],5500),

    # ══════════════════════════════════════════════════════════════════
    # CARTIER
    # ══════════════════════════════════════════════════════════════════
    w("car-st-wsst0003","Cartier","Santos","WSST0003","2018–present","Cal. 1847 MC","39.8mm",["santos","steel","quick-release"],5500),
    w("car-st-wgsa0054","Cartier","Santos Large","WGSA0054","2018–present","Cal. 1847 MC","39.8mm",["santos","gold","luxury"],14000),
    w("car-st-wssa0018","Cartier","Santos WSSA0018","WSSA0018","2019–present","Cal. 1847 MC","39.8mm",["santos","steel","pasha"],5500),
    w("car-pa-wspa0013","Cartier","Pasha de Cartier","WSPA0013","2020–present","Cal. 1847 MC","41mm",["pasha","steel","screw-crown"],6000),
    w("car-pa-crw2020052","Cartier","Pasha Chronograph","CRWS0010","2021–present","Cal. 1904-CH MC","41mm",["pasha","chronograph","steel"],8500),
    w("car-ro-wsro0002","Cartier","Ronde Louis Cartier","WSRN0002","2012–present","Cal. 430 MC","42mm",["ronde-louis","steel","classic"],5000),
    w("car-ta-wsft0003","Cartier","Tank Must","WSFT0003","2021–present","Cal. 1847 MC","33.7×25.5mm",["tank","must","steel"],3200),
    w("car-ta-wsta0060","Cartier","Tank Française","WSTA0060","2017–present","Cal. 157","28×23.9mm",["tank","francaise","steel","ladies"],4000),
    w("car-ta-wgta0064","Cartier","Tank Américaine","WGTA0064","2020–present","Cal. 1904 PS MC","34.4×27.4mm",["tank","americaine","gold"],16000),
    w("car-ba-wgba0010","Cartier","Ballon Bleu","WGBB0030","2007–present","Cal. 076","33mm",["ballon-bleu","rose-gold","ladies"],12000),
    w("car-ba-w6920046","Cartier","Ballon Bleu 42","W6920046","2013–present","Cal. 1847 MC","42mm",["ballon-bleu","steel"],5500),

    # ══════════════════════════════════════════════════════════════════
    # JAEGER-LECOULTRE
    # ══════════════════════════════════════════════════════════════════
    w("jlc-rm-q1538420","Jaeger-LeCoultre","Reverso Classic Large","Q1538420","2011–present","Cal. 822","47×27.4mm",["reverso","classic","steel"],8500),
    w("jlc-rm-q3848422","Jaeger-LeCoultre","Reverso Tribute Calendar","Q3848422","2015–present","Cal. 853","49.4×29.9mm",["reverso","tribute","calendar","steel"],18000),
    w("jlc-rm-q3858402","Jaeger-LeCoultre","Reverso Tribute Moon","Q3858402","2015–present","Cal. 854A","49.4×29.9mm",["reverso","tribute","moonphase","steel"],15000),
    w("jlc-mt-q1368420","Jaeger-LeCoultre","Master Ultra Thin","Q1368420","2013–present","Cal. 849","39mm",["master","ultra-thin","steel"],8000),
    w("jlc-mt-q1362520","Jaeger-LeCoultre","Master Ultra Thin Perpetual","Q1362520","2014–present","Cal. 866","39mm",["master","perpetual-calendar","steel"],22000),
    w("jlc-mt-q4018480","Jaeger-LeCoultre","Master Control Date","Q4018480","2020–present","Cal. 899","40mm",["master","control","date","steel"],6000),
    w("jlc-po-q3668430","Jaeger-LeCoultre","Polaris Automatic","Q3668430","2018–present","Cal. 899/1","42mm",["polaris","diver","steel"],6500),
    w("jlc-po-q9068680","Jaeger-LeCoultre","Polaris Chronograph","Q9068680","2018–present","Cal. 751","42mm",["polaris","chronograph","steel"],9000),
    w("jlc-at-q9008481","Jaeger-LeCoultre","Atmos Classique","Q5102201","2000–present","Cal. 563","220×175×148mm",["atmos","clock","mantel"],5500),

    # ══════════════════════════════════════════════════════════════════
    # A. LANGE & SÖHNE
    # ══════════════════════════════════════════════════════════════════
    w("als-lang-101039","A. Lange & Söhne","Lange 1","101.039","1994–present","Cal. L901.0","38.5mm",["lange1","dress","yellow-gold"],48000),
    w("als-lang-101026","A. Lange & Söhne","Lange 1","101.026","1994–present","Cal. L901.0","38.5mm",["lange1","dress","white-gold"],55000),
    w("als-lang-101032","A. Lange & Söhne","Lange 1","101.032","2010–present","Cal. L901.0","38.5mm",["lange1","dress","platinum"],75000),
    w("als-sa-381032","A. Lange & Söhne","Saxonia Thin","211.032","2012–present","Cal. L093.1","40mm",["saxonia","thin","white-gold"],28000),
    w("als-dt-386032","A. Lange & Söhne","Datograph Perpetual","410.025","2009–present","Cal. L952.1","41mm",["datograph","perpetual","flyback","platinum"],195000),
    w("als-dt-403035","A. Lange & Söhne","Datograph Up/Down","405.035","2012–present","Cal. L951.6","41mm",["datograph","up-down","rose-gold"],85000),
    w("als-ro-101060","A. Lange & Söhne","Richard Lange","232.032","2006–present","Cal. L041.2","40.9mm",["richard-lange","white-gold","classic"],55000),
    w("als-1815","A. Lange & Söhne","1815","233.025","2013–present","Cal. L051.1","38.5mm",["1815","rose-gold","dress"],45000),
    w("als-zb-725032","A. Lange & Söhne","Zeitwerk","140.032","2009–present","Cal. L043.1","41.9mm",["zeitwerk","digital","jumping-hour","white-gold"],95000),

    # ══════════════════════════════════════════════════════════════════
    # HUBLOT
    # ══════════════════════════════════════════════════════════════════
    w("hub-bm-301sx130rx","Hublot","Big Bang Unico","301.SX.130.RX","2012–present","Cal. UNICO","44mm",["big-bang","unico","ceramic","chronograph"],18000),
    w("hub-bm-411px170rx","Hublot","Big Bang Unico Platinum","411.PX.170.RX","2013–present","Cal. UNICO","45mm",["big-bang","unico","platinum"],55000),
    w("hub-bm-342pb131rv","Hublot","Classic Fusion","542.PX.130.LR","2016–present","Cal. HUB1110","45mm",["classic-fusion","titanium"],12000),
    w("hub-bm-542cm17010","Hublot","Classic Fusion Aerofusion","525.NX.0170.LR","2014–present","Cal. HUB1155","45mm",["classic-fusion","aerofusion","chronograph"],18000),
    w("hub-sp-601ox0170","Hublot","Spirit of Big Bang","601.OX.0183.LR","2014–present","Cal. HUB4700","42mm",["spirit","big-bang","rose-gold"],28000),

    # ══════════════════════════════════════════════════════════════════
    # ZENITH
    # ══════════════════════════════════════════════════════════════════
    w("zen-el-03212040051c496","Zenith","El Primero 36'000","03.2110.400/69.C496","2011–present","Cal. El Primero 400","42mm",["el-primero","chronograph","steel"],5500),
    w("zen-ch-03212400051c493","Zenith","Chronomaster Original","03.3200.3600/69.M3200","2021–present","Cal. El Primero 3600","38mm",["chronomaster","original","vintage","steel"],5000),
    w("zen-de-95214005001c759","Zenith","Defy Classic","95.9000.670/78.R584","2017–present","Cal. Elite 670 SK","41mm",["defy","classic","skeleton","steel"],7500),
    w("zen-de-87216809701c765","Zenith","Defy Extreme","87.9100.9004/01.I001","2021–present","Cal. ZO 342","45mm",["defy","extreme","carbon","chronograph"],15000),
    w("zen-pi-032430400451c496","Zenith","Pilot Type 20 Annual Calendar","03.2430.4054/21.C721","2017–present","Cal. El Primero 4054","45mm",["pilot","annual-calendar","steel"],9000),
    w("zen-de-defylab","Zenith","Defy Lab","00.9000.8812/78.R582","2017","Cal. Oscillator","44mm",["defy","lab","oscillator","limited"],35000),

]

# Rimuovi eventuali duplicati per reference
seen = set()
unique = []
for watch in catalog:
    key = (watch["brand"], watch["reference"])
    if key not in seen:
        seen.add(key)
        unique.append(watch)

out = pathlib.Path(__file__).parent / "watches.json"
out.write_text(json.dumps(unique, ensure_ascii=False, indent=2))
print(f"Scritto {len(unique)} referenze in {out}")

# Stampa riepilogo per brand
from collections import Counter
counts = Counter(w["brand"] for w in unique)
for brand, n in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {brand:<30} {n:>3}")
