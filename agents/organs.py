class Organ:
    registry = []
    def __init__(self, exchange_obligation,organ_id, donor_row):
        self.organ_id= organ_id
        if donor_row["GRAFT_TYPE"]== "KD":
            self.type = "kidney"
        else:
            self.type = "undefined"
        self.donor_id = donor_row["DONORNUMBER"]
        self.exchange_obligation = exchange_obligation
        self.timestep = donor_row["TIMESTEP_ENTERED"]
        
        self.abo_blood=donor_row["AB0_BLOOD_GROUP"]
        self.rhesus= donor_row["RHESUS_CODE"]
        
        self.city=donor_row["CITY"]
        self.country=donor_row["COUNTRY"]
        self.donor_row= donor_row

        self.geno_HLA_A=donor_row["Genomic_HLA-A"]
        self.geno_HLA_B=donor_row["Genomic_HLA-B"]
        self.geno_HLA_C=donor_row["Genomic_HLA-C"]
        self.geno_HLA_DRB1=donor_row["Genomic_HLA-DRB1"]
        self.geno_HLA_DQA1=donor_row["Genomic_HLA-DQA1"]
        self.geno_HLA_DQB1=donor_row["Genomic_HLA-DQB1"]
        self.geno_HLA_DPA1=donor_row["Genomic_HLA-DPA1"]
        self.geno_HLA_DPB1=donor_row["Genomic_HLA-DPB1"]

        self.donor_age= donor_row["AGE"]
        #All organs self register on the registry on creation
        Organ.registry.append(self)
    def print(self):
        print("*******************************")
        print(f"Organ Type: {self.type}")
        print(f"Donor ID: {self.donor_id}")
        print(f"Exchange Obligation: {self.exchange_obligation}")
        print(f"Timestep Entered: {self.timestep}")
        print(f"Blood Group: {self.abo_blood} {self.rhesus}")
        print(f"Location: {self.city}, {self.country}")
        print("*******************************")