import pandas as pd
import numpy as np
import os

watch_brands = set()

brands = [
    "A.Lange & Söhne", "Alpina", "Audemars Piguet",
    "Bell & Ross", "Blancpain", "Breguet", "Breitling", "Bulova", "Baume & Mercier", "Bulgari",
    "Casio", "Chanel", "Christopher Ward", "Citizen", "Chopard", "Cartier", "Certina","Chronoswiss", "Corum",
    "Doxa", "Davosa",
    "Ebel", "Eberhard & Co.",
    "Franck Muller", "Fredrique Constant",
    "Girard-Perregaux", "Glashütte Original", "Gucci", "Grand Seiko",
    "Heuer", "Hamilton", "Hermès", "Hublot",
    "IWC",
    "Jaeger-LeCoultre", "Jacob & Co.", "Junghans",
    "Longines", "Luminox", "Lorus",
    "Maurice Lacroix", "Montblanc", "Mido", "Movado", "Meistersinger",
    "NOMOS",
    "Omega", "Oris", "Orient",
    "Paul Picot", "Piaget", "Panerai", "Patek Philippe", "Porsche Design",
    "Rado", "Raymond Weil", "Richard Mille", "Rolex",
    "Seiko", "Sinn", "Swatch", "Spinnaker", "Swiss Military", "Squale", "Steinhart",
    "TAG Heuer", "Tissot", "Timex", "Tudor",
    "Ulysse Nardin",
    "Vacheron Constantin", "Venezianico", "Versace", "Vostok", "Victorinox Swiss Army", "Vulcain",
    "Yema",
    "Zenith", "Zodiac"
]

for brand_name in brands:
    watch_brands.add(brand_name)

def preprocess_data(file_path = "../resources/watches_data_new.csv"):
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Convert 'price' to numeric, forcing errors to NaN
    df['price'] = pd.to_numeric(df['price'], errors='coerce')

    # Drop rows with NaN values in the 'price' column after conversion
    df.dropna(subset=['price', 'model'], inplace=True)

    # Create a brand column, from the 'model' column based on the watch_brands set
    df['brand'] = df['model'].apply(lambda x: next((brand for brand in watch_brands if brand in x), None))

    # Drop rows where brand is None
    df.dropna(subset=['brand'], inplace=True)

    df_cleaned = df.copy()

    # Iterate through each row and remove the brand name from the model
    for index, row in df.iterrows():
        brand = row['brand']
        model = row['model']

        # If the brand appears in the model name, remove it
        if brand in model:
            # Strip any leading spaces that might remain
            df_cleaned.at[index, 'model'] = model.replace(brand, '').strip()

    cols = list(df_cleaned.columns)
    cols.insert(0, cols.pop(cols.index('brand')))
    df_cleaned = df_cleaned[cols]

    # Modify the diameter column so that only the first value is considered if it has an "x" in it
    df_cleaned['case_diameter'] = df_cleaned['case_diameter'].apply(lambda x: x.split('x')[0] if 'x' in str(x) else x)
    # Also, split the diameter by "mm" and keep only the first part, stripped and converted to float
    df_cleaned['case_diameter'] = df_cleaned['case_diameter'].apply(lambda x: str(x).split('mm')[0].strip() if 'mm' in str(x) else x)
    # Convert the diameter to numeric, forcing errors to NaN
    df_cleaned['case_diameter'] = pd.to_numeric(df_cleaned['case_diameter'], errors='coerce')

    # Fix the model column by filling missing values
    df_cleaned = fix_model(df_cleaned)
    df_fixed = fix_model(df_cleaned)

    df_fixed.to_csv("../resources/cleaned_watches_data.csv", index=False)


# Fill the missing model values, based on the most abundant model for that brand
def fix_model(df: pd.DataFrame):
    df_copy = df.copy()

    # Compute the most abundant model per brand, ensuring empty cases are handled
    most_abundant_models = df_copy.groupby('brand')['model'].apply(
        lambda x: x.value_counts().idxmax() if not x.dropna().empty else None
    ).to_dict()

    # Fill missing model values based on the most abundant model for that brand, if available
    for index, row in df_copy.iterrows():
        if pd.isnull(row['model']):
            brand = row['brand']
            if brand in most_abundant_models and most_abundant_models[brand] is not None:
                df_copy.at[index, 'model'] = most_abundant_models[brand]

    # Drop rows with NaN values in the 'model' column
    df_copy.dropna(subset=['model'], inplace=True)

    # Fill the case diameter column with 40 if it is NaN
    df_copy.fillna({'case_diameter': 40}, inplace=True)

    return df_copy


def prepare_model_features(df: pd.DataFrame) -> pd.DataFrame:
    # Create a new DataFrame to hold the features
    df_features = pd.DataFrame()

    # Take the brand, model, price, shipping_cost, movement, case_material,
    # year_of_production, condition, scope_of_delivery, case_diameter, and country_code columns
    df_features['brand'] = df['brand']
    df_features['model'] = df['model']
    df_features['price'] = df['price']
    df_features['movement'] = df['movement']
    df_features['case_material'] = df['case_material']
    df_features['year_of_production'] = df['year_of_production']
    df_features['condition'] = df['condition']
    df_features['scope_of_delivery'] = df['scope_of_delivery']
    df_features['case_diameter'] = df['case_diameter']
    df_features['country_code'] = df['country_code']

    return df_features


def get_model_df(path = "../resources/cleaned_watches_data_fixed.csv"):
    # Read the cleaned watches data
    df = pd.read_csv(path)

    # Prepare the model features
    df_features = prepare_model_features(df)

    def parse_year(year_str):
        if year_str == "-" or pd.isna(year_str):
            return np.nan  # Unknown year
        try:
            return float(year_str)  # Convert known years to float
        except ValueError:
            return np.nan  # Handle any other unexpected formats

    df_features['year_of_production'] = df_features['year_of_production'].apply(parse_year)

    # We'll add a flag to indicate if the year is missing
    df_features['year_unknown'] = df_features['year_of_production'].isna().astype(int)

    # Impute missing years with the median year
    median_year = df_features['year_of_production'].median()
    df.fillna({'year_of_production': median_year}, inplace=True)

    # Convert price to numeric, forcing errors to NaN
    df_features['price'] = pd.to_numeric(df_features['price'], errors='coerce')

    # Drop the prices greater than 3 million
    df_features = df_features[df_features['price'] <= 3000000]

    # Fill the nan years with the median year
    df_features.fillna({'year_of_production': median_year}, inplace=True)

    # Rank the condition column
    # ['Like new & unworn' 'Very good' 'New' 'Good' 'Fair' '-' 'Incomplete', 'Poor']
    condition_ranking = {
        'Like new & unworn': 1,
        'Very good': 2,
        'New': 3,
        'Good': 4,
        'Fair': 5,
        '-': 6,
        'Incomplete': 7,
        'Poor': 8
    }
    df_features['condition'] = (
        df_features['condition']
        .map(condition_ranking)  # Use map instead of replace
        .astype(int)  # Explicitly convert to int (optional but safe)
    )

    # Rank the scope_of_delivery column
    # ['Original box, original papers' 'Original box, no original papers', 'No original box, no original papers' 'Original papers, no original box']
    scope_ranking = {
        'Original box, original papers': 1,
        'Original box, no original papers': 3,
        'No original box, no original papers': 4,
        'Original papers, no original box': 2
    }
    df_features['scope_of_delivery'] = (
        df_features['scope_of_delivery']
        .map(scope_ranking)  # Use map instead of replace
        .astype(int)  # Explicitly convert to int (optional but safe)
    )

    return df_features

def save_brand_avg_prices():
    # get the path of the currently working file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "..", "resources", "brand_avg_prices.csv")

    # Read the cleaned watches data
    df = get_model_df()
    # Calculate the average price per brand
    avg_prices = df.groupby('brand')['price'].mean().reset_index()
    # Save the average prices to a CSV file
    avg_prices.to_csv(csv_path, index=False)

def save_model_avg_prices():
    # Get the path of the currently working file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "..", "resources", "model_avg_prices.csv")

    # Read the cleaned watches data
    df = get_model_df()

    # Calculate the average price per model
    avg_prices = df.groupby('model')['price'].mean().reset_index()

    # Get one product_url per model (first occurrence)
    urls = df.groupby('model')['product_url'].first().reset_index()

    # Merge the two DataFrames on 'model'
    result = pd.merge(avg_prices, urls, on='model')

    # Save the result to a CSV file
    result.to_csv(csv_path, index=False)

def get_model_avg_price(model, brand):
    try:
        # get the path of the currently working file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, "..", "resources", "model_avg_prices.csv")

        # Read the cleaned watches data
        df = pd.read_csv(csv_path)
        # Calculate the average price per brand
        avg_price = df[df['model'] == model]['price'].values[0]

        return avg_price

    except Exception as e:
        return get_brand_avg_price(brand)

def get_brand_avg_price(brand):
    # get the path of the currently working file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "..", "resources", "brand_avg_prices.csv")

    # Read the cleaned watches data
    df = pd.read_csv(csv_path)
    # Calculate the average price per brand
    avg_price = df[df['brand'] == brand]['price'].values[0]

    return avg_price


if __name__ == '__main__':

    # preprocess_data()
    #
    # df_fixed = fix_model(pd.read_csv("../resources/cleaned_watches_data.csv"))
    # df_fixed.to_csv("../resources/cleaned_watches_data_fixed.csv", index=False)

    # save_brand_avg_prices()

    save_model_avg_prices()



