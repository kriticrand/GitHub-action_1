from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import re

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        # Read file content
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode("utf-8")), skip_blank_lines=True)

        # Standardize column names: remove leading/trailing spaces, lowercase
        df.columns = [col.strip().lower() for col in df.columns]

        # Find likely category and amount columns
        category_col = next(col for col in df.columns if "category" in col)
        amount_col = next(col for col in df.columns if "amount" in col or "price" in col)

        # Clean category column (strip and lowercase)
        df[category_col] = df[category_col].astype(str).str.strip().str.lower()

        # Clean amount column: remove commas, currency symbols, convert to float
        df[amount_col] = (
            df[amount_col]
            .astype(str)
            .str.replace(",", "")
            .str.replace(r"[^\d.\-]", "", regex=True)
            .astype(float)
        )

        # Filter for 'food' category only
        food_df = df[df[category_col].str.lower() == "food"]

        # Calculate total
        total = food_df[amount_col].sum()

        return JSONResponse(
            content={
                "answer": round(total, 2),
                "email": "24f1001182@ds.study.iitm.ac.in",
                "exam": "tds-2025-05-roe",
            }
        )

    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Failed to process file: {str(e)}"})
