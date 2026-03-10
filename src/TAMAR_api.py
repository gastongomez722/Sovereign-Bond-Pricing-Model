
def get_tamar_daily():
    ''' this function uses a request to the BCRA website to download the daily TAMAR
    returns the data as a pandas dataframe, since the beginning of measurement
    note: TAMAR is only published on business days
    '''
    BCRA_DIAR_PAS_URL = "https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/diar_pas.xls"
    # Define headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # 1. Download the Excel file with added headers
    resp = requests.get(BCRA_DIAR_PAS_URL, verify=False, headers=headers)
    resp.raise_for_status()

    # 2. Load into pandas, specifying the engine for .xls files
    xls = pd.ExcelFile(io.BytesIO(resp.content), engine='xlrd')

    # Use the specified sheet name
    sheet_name = 'Totales_diarios'
    df = xls.parse(sheet_name, header=35)

    # Clean / standardize columns by stripping whitespace and replacing newlines
    df.columns = [str(c).strip().replace('\n', ' ') for c in df.columns]

    # Identify the column 'Ah' (index 33) and the date column (index 0)
    date_col_name = df.columns[0]
    # Column 'AH' is at index 33
    tamar_col_name = df.columns[33]

    out = df[[date_col_name, tamar_col_name]].copy()

    # Convert date column to datetime objects, specifying dayfirst=True for Argentinian format
    out[date_col_name] = pd.to_datetime(out[date_col_name], errors='coerce', dayfirst=True)

    # Drop rows where date conversion failed (e.g., non-data rows below the actual data)
    out.dropna(subset=[date_col_name], inplace=True)

    # Set date column as index and sort
    out = out.sort_values(date_col_name).set_index(date_col_name)

    # Rename the data column to 'TAMAR' for consistency
    out.rename(columns={tamar_col_name: 'TAMAR'}, inplace=True)

    return out
