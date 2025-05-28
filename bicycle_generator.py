def generate_bicycles_stream(xlsx_path: str):
    import pandas as pd
    from itertools import product

    # Load the entire Excel workbook
    xls = pd.ExcelFile(xlsx_path)

    # === Read and clean the ID sheet ===
    id_df = pd.read_excel(xls, sheet_name="ID", dtype=str).fillna("").applymap(str.strip)

    # Extract valid values from each column (ignoring blanks)
    designator_names = list(id_df.columns)
    designator_values = []
    for col in designator_names:
        unique_values = sorted(set(val for val in id_df[col] if val.strip()))
        designator_values.append(unique_values)

    # Generate all valid permutations
    permutations = product(*designator_values)

    # === Load GENERAL sheet ===
    general_df = pd.read_excel(xls, sheet_name="GENERAL", dtype=str).fillna("")
    general_fields = general_df.iloc[0].to_dict()
    general_fields = {k: str(v).strip() for k, v in general_fields.items()}

    # === Load all designator-dependent sheets ===
    designator_sheets = {}
    designator_sheet_fields = {}
    for designator in designator_names:
        if designator == "Model number":
            continue  # Skip sheet for Model number

        try:
            sheet_df = pd.read_excel(xls, sheet_name=designator, dtype=str).fillna("").applymap(str.strip)
        except Exception:
            # Try to load by index fallback
            sheet_idx = designator_names.index(designator)
            sheet_df = pd.read_excel(xls, sheet_name=sheet_idx+1, dtype=str).fillna("").applymap(str.strip)

        sheet_df.columns = sheet_df.columns.map(str)
        key_col = sheet_df.columns[0]
        sheet_df[key_col] = sheet_df[key_col].astype(str).str.strip()
        sheet_df = sheet_df.set_index(key_col)
        sheet_df.index = sheet_df.index.map(str).str.strip()
        designator_sheets[designator] = sheet_df
        designator_sheet_fields[designator] = [col for col in sheet_df.columns if col != key_col]

    # === Collect all fields from all sheets ===
    all_designator_fields = set()
    for fields in designator_sheet_fields.values():
        all_designator_fields.update(fields)

    # === Generate all bicycle configurations ===
    for combo in permutations:
        bike = {}

        # Construct full ID
        id_parts = [str(part).strip() for part in combo]
        bike_id = ''.join(id_parts)
        bike["ID"] = bike_id

        # Add general fields
        bike.update(general_fields)

        # Populate designator-specific fields
        idx = 0
        for value, designator in zip(combo, designator_names):
            value = str(value)
            length = len(value)
            parsed_value = bike_id[idx:idx + length]
            idx += length

            if designator == "Model number":
                continue

            sheet = designator_sheets[designator]
            fields = designator_sheet_fields[designator]

            if parsed_value in sheet.index:
                row = sheet.loc[parsed_value]
                if isinstance(row, pd.DataFrame):
                    row = row.iloc[0]
                for col in fields:
                    raw_val = row.get(col, "")
                    bike[col] = str(raw_val).strip() if pd.notna(raw_val) else ""
            else:
                print(f"Warning: Value '{parsed_value}' not found in sheet '{designator}'")
                for col in fields:
                    bike[col] = ""

        # Ensure all expected fields are present
        for col in all_designator_fields:
            if col not in bike:
                bike[col] = ""

        # Final cleanup
        for key in bike:
            bike[key] = str(bike[key]).replace("\u00b0", "°").replace("\u2033", "\"")

        yield bike
