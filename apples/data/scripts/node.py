#categories
# 1: flight between non-hub airports
# 2: flight between class 1 airports


# flights are going to need to take directionality into account, because the weight based hub size is directional

class Node:
    def __init__(self):(fips, category, state, county)
        self.fips = fips
        self.category = category
        self.state = state
        self.county = county
