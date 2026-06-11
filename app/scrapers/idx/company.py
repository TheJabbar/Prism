from datetime import datetime
from app.scrapers.idx.idx_client import idx_get


async def get_stock_screener(sector: str = "", sub_sector: str = ""):
    data = await idx_get(
        f"https://www.idx.co.id/support/stock-screener/api/v1/stock-screener/get?Sector={sector}&SubSector={sub_sector}"
    )
    if not data or not isinstance(data.get("results"), list):
        return None
    return [
        {
            "code": i.get("stockCode", ""),
            "name": i.get("companyName", ""),
            "sector": i.get("sector", ""),
            "subSector": i.get("subSector", ""),
            "industry": i.get("industry", ""),
            "marketCap": i.get("marketCapital", 0),
            "revenue": i.get("tRevenue", 0),
            "per": i.get("per", 0),
            "pbv": i.get("pbv", 0),
            "der": i.get("der", 0),
            "roa": i.get("roa", 0),
            "roe": i.get("roe", 0),
            "npm": i.get("npm", 0),
            "week4": i.get("week4PC", 0),
            "week13": i.get("week13PC", 0),
            "week26": i.get("week26PC", 0),
            "week52": i.get("week52PC", 0),
            "ytd": i.get("ytdpc", 0),
            "mtd": i.get("mtdpc", 0),
            "status": i.get("status"),
            "notation": i.get("notation"),
            "corpAction": i.get("corpAction"),
        }
        for i in data["results"]
    ]


async def get_financial_ratios(year: int | None = None, month: int | None = None):
    now = datetime.now()
    y = year or now.year
    m = month or now.month
    data = await idx_get(
        f"https://www.idx.co.id/primary/DigitalStatistic/GetApiDataPaginated?urlName=LINK_FINANCIAL_DATA_RATIO&periodYear={y}&periodMonth={m}&periodType=monthly&isPrint=False&cumulative=false"
    )
    if not data or not isinstance(data.get("data"), list):
        return None
    return [
        {
            "code": i.get("code", ""),
            "name": i.get("stockName", ""),
            "sector": i.get("sector", ""),
            "subSector": i.get("subSector", ""),
            "period": i.get("fsDate", ""),
            "assets": i.get("assets", 0),
            "liabilities": i.get("liabilities", 0),
            "equity": i.get("equity", 0),
            "sales": i.get("sales", 0),
            "profit": i.get("profitPeriod", 0),
            "eps": i.get("eps", 0),
            "bookValue": i.get("bookValue", 0),
            "per": i.get("per", 0),
            "pbv": i.get("priceBV", 0),
            "der": i.get("deRatio", 0),
            "roa": i.get("roa", 0),
            "roe": i.get("roe", 0),
            "npm": i.get("npm", 0),
        }
        for i in data["data"]
    ]


async def get_company_profiles(start: int = 0, length: int = 9999):
    data = await idx_get(
        f"https://www.idx.co.id/primary/ListedCompany/GetCompanyProfiles?start={start}&length={length}"
    )
    if not data or not isinstance(data.get("data"), list):
        return None
    return [
        {
            "code": i.get("KodeEmiten", ""),
            "name": i.get("NamaEmiten", ""),
            "listingDate": i.get("TanggalPencatatan", ""),
        }
        for i in data["data"]
    ]


async def get_company_detail(code: str, language: str = "id-id"):
    data = await idx_get(
        f"https://www.idx.co.id/primary/ListedCompany/GetCompanyProfilesDetail?KodeEmiten={code}&language={language}"
    )
    if not data or not data.get("Profiles"):
        return None
    p = data["Profiles"][0]
    return {
        "code": p.get("KodeEmiten", ""),
        "name": p.get("NamaEmiten", ""),
        "sector": p.get("Sektor", ""),
        "subSector": p.get("SubSektor", ""),
        "industry": p.get("Industri", ""),
        "board": p.get("PapanPencatatan", ""),
        "listingDate": p.get("TanggalPencatatan", ""),
        "status": p.get("Status", ""),
        "address": p.get("Alamat", ""),
        "phone": p.get("Telepon", ""),
        "email": p.get("Email", ""),
        "website": p.get("Website", ""),
        "businessActivity": p.get("KegiatanUsahaUtama", ""),
        "directors": [
            {"name": d.get("Nama", ""), "position": d.get("Jabatan", "")}
            for d in (data.get("Direktur") or [])
        ],
        "commissioners": [
            {"name": d.get("Nama", ""), "position": d.get("Jabatan", "")}
            for d in (data.get("Komisaris") or [])
        ],
        "shareholders": [
            {"name": s.get("Nama", ""), "percentage": s.get("Persentase", 0)}
            for s in (data.get("PemegangSaham") or [])
        ],
    }
