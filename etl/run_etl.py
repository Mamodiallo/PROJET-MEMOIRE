from pathlib import Path
from etl.load import load_raw
from etl.clean import clean_df
from etl.recode import recode_df
from etl.export import export_clean

def run_etl():
    raw_path = Path("data/1_raw/AMV_GDT_P3M.csv")
    print("CWD       →", Path().resolve())
    print("Searching →", raw_path, "| exists?", raw_path.exists())
    clean_path = Path("data/2_processed/cleaned_AMV_GDT_P3M.csv")

    df = load_raw(raw_path)
    df = clean_df(df)
    df = recode_df(df)
    export_clean(df, clean_path)
    
    print("etl terminé →", clean_path)
    
if __name__ == "__main__":
    
    run_etl()
