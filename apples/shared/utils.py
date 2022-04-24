import os
from pathlib import Path

US_STATES = { 'ALASKA':'AK','ALABAMA': 'AL', 'ARKANSAS':'AR', 'ARIZONA': 'AZ', 'CALIFORNIA':'CA',
        'COLORADO': 'CO', 'CONNECTICUT': 'CT', 'WASHINGTON DC':'DC', 'DELAWARE': 'DE', 
        'FLORIDA': 'FL', 'GEORGIA': 'GA', 'HAWAII': 'HI', 'IDAHO': 'ID', 'ILLINOIS': 'IL', 
        'INDIANA': 'IN', 'IOWA': 'IA', 'KANSAS': 'KS', 'KENTUCKY': 'KY', 'LOUISIANA': 'LA', 
        'NEBRASKA': 'NE', "NEVADA": 'NV', 'NEW HAMPSHIRE': 'NH', 
        'NEW JERSEY': 'NJ', 'NEW MEXICO': 'NM', 'NEW YORK': 'NY', 'NORTH CAROLINA': 'NC', 
        'NORTH DAKOTA': 'ND', 'OHIO': 'OH', 'OKLAHOMA': 'OK', 'OREGON': 'OR', 'MARYLAND': 'MD', 
        'MAINE': 'ME', 'MONTANA': 'MT', 'MASSACHUSETTS': 'MA', 'MICHIGAN': 'MI', 'MINNESOTA': 'MN', 
        'MISSISSIPPI': 'MS', 'MISSOURI':'MO', 'PENNSYLVANIA': 'PA', 'RHODE ISLAND': 'RI', 
        'SOUTH CAROLINA': 'SC', 'SOUTH DAKOTA': 'SD', 'TENNESSEE': 'TN', 'TEXAS': 'TX', 'UTAH': 'UT',
        'VERMONT': 'VT', 'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WEST VIRGINIA': 'WV', 'WISCONSIN': 'WI', 
        'WYOMING': 'WY' }
US_STATE_FIPS = { 'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06', 'CO': '08', 'CT': '09', 'DE': '10', 'FL': '12', 'GA': '13', 'HI': '15', 'ID': '16', 'IL': '17', 'IN': '18', 'IA': '19', 'KS': '20', 'KY': '21', 'LA': '22', 'ME': '23', 'MD': '24', 'MA': '25', 'MI': '26', 'MN': '27', 'MS': '28', 'MO': '29', 'MT': '30', 'NE': '31', 'NV': '32', 'NH': '33', 'NJ': '34', 'NM': '35', 'NY': '36', 'NC': '37', 'ND': '38', 'OH': '39', 'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44', 'SC': '45', 'SD': '46', 'TN': '47', 'TX': '48', 'UT': '49', 'VT': '50', 'VA': '51', 'WA': '53', 'WV': '54', 'WI': '55', 'WY': '56' } 

FIPS_US_STATE = {v: k for k, v in US_STATE_FIPS.items()}

def get_project_root() -> Path:
    return Path(__file__).parent.parent

def get_resource_dir() -> Path:
    root = get_project_root()
    return root.joinpath("resources")

def normalize_name(name):

    # if the name given is combined, choose the first. Dual names like this are either in the same FIPS or the same CBSA
    if name.find("/"):
        name = name.partition('/')[0]

    # upcase name
    name = name.upper()

    # standardize all saints
    name = name.replace("ST.", "SAINT")

    # there's only one 'sainte' but it gets the treatment too
    name = name.replace("STE.", "SAINTE")

    # strip the trailing "county"
    name = name.removesuffix(' COUNTY')

    # remove periods
    name = name.replace('.','')
    # remove single quotes
    name = name.replace("'", "")
    # remove empty spaces in name 
#    name = name.replace(" ", "")

    # remove dashes from name 
    # UNSURE if I want this yet
    #name = name.replace("-", "")

    return name
