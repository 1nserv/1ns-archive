class NSID(str):
    unknown = "0"
    admin = "01"
    gov = "02"
    assembly = "03"
    court = "04"
    office = "05"
    hexabank = "06"
    archives = "07"

    maintenance_committee = "101"
    audiovisual_department = "102"
    interior_department = "103"

    def __new__(cls, value):
        if type(value) == int:
            value = hex(value)
        elif type(value) in (str, NSID):
            value = hex(int(value, 16))
        else:
            return TypeError(f"<{value}> is not NSID serializable")
        
        if value.startswith("0x"):
            value = value[2:]
        
        instance = super(NSID, cls).__new__(cls, value.upper())
        return instance