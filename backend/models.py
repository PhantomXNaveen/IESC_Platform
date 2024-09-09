from flask_sqlalchemy  import SQLAlchemy

db = SQLAlchemy() # Instance of SQLAlchemy

class Influencers(db.Model):
    __tablename__="influencers"
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String,unique=True,nullable=False)
    name=db.Column(db.String,nullable=False)
    email=db.Column(db.String,nullable=False,unique=True)
    pwd=db.Column(db.String,nullable=False)
    niche=db.Column(db.String,nullable=False,default="Other")
    platform=db.Column(db.String,nullable=False,default="Other")
    followers=db.Column(db.Integer,nullable=False)
    flagged=db.Column(db.String,nullable=False,default="NO") 

    influencer = db.relationship('Ad_requests', backref='influencer')
    
    def set_niche(self, niche):
        if niche not in ["Fashion", "Technology","Travel","Food","Fitness","Beauty","Lifestyle","Other"]:
            raise ValueError("Select a Niche")
        self.niche = niche

    def set_platform(self, platform):
        if platform not in ["Youtube", "Instagram","Instagram","Other"]:
            raise ValueError("Select a Platform ")
        self.platform = platform


class Sponsors(db.Model):
    __tablename__="sponsors" 
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String,unique=True,nullable=False)
    name=db.Column(db.String,nullable=False)
    email=db.Column(db.String,nullable=False,unique=True)
    pwd=db.Column(db.String,nullable=False)
    industry=db.Column(db.String,nullable=False,default="Other")
    budget=db.Column(db.Integer,nullable=False)   
    flagged=db.Column(db.String,nullable=False,default="NO")
    # A Sponsor can have many campaigns | backref = 'sponsor'creates a 'sponsor' attribute on 'Campaigns' model allowing access to 'sponsor' object from 'campaign' instance 
    campaigns = db.relationship('Campaigns',backref='sponsor')

    def set_industry(self, industry):
        if industry not in ["Fashion", "Technology","Travel","Food","Fitness","Beauty","Lifestyle","Other"]:
            raise ValueError("Select a Industry")
        self.industry = industry

class Admin(db.Model):
    __tablename__="admin"
    id=db.Column(db.Integer,primary_key=True)
    user_name=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)


class Campaigns(db.Model):
    __tablename__="campaigns" 
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String,nullable=False)
    description=db.Column(db.Text,nullable=False)
    start_date=db.Column(db.String,nullable=False)
    end_date=db.Column(db.String,nullable=False)
    budget=db.Column(db.Integer,nullable=False)
    visibility = db.Column(db.String, nullable=False, default="Public")
    goal=db.Column(db.String,nullable=False)
    niche=db.Column(db.String,nullable=False,default="Other")
    flagged=db.Column(db.String,nullable=False,default="NO")

    # Foreign Key to link Sponsors(refer to primary key of sponsor)
    sponsor_id=db.Column(db.Integer,db.ForeignKey('sponsors.id'),nullable=False)

    campaign = db.relationship('Ad_requests', backref='campaign')

    def set_visibility(self, visibility):
        if visibility not in ["Public", "Private"]:
            raise ValueError("Visibility must be 'Public' or 'Private'")
        self.visibility = visibility

    def set_niche(self, niche):
        if niche not in ["Fashion", "Technology","Travel","Food","Fitness","Beauty","Lifestyle","Other"]:
            raise ValueError("Select a Niche")
        self.niche = niche

# ------------------------------------------------------------------------------------------------------------------------------------------


class Ad_requests(db.Model):
    __tablename__ = "ad_requests"
    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String, nullable=True)
    message = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Integer, nullable=False)
    status_influencer = db.Column(db.String,nullable=False, default='Pending')
    status_sponsor = db.Column(db.String,nullable=False, default='Pending')
    
    # Foreign key to the Campaign table
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'),nullable=False)
    
    # Foreign key to the Influencer table
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencers.id'),nullable=False)

    def set_status_influencer(self,status_influencer):
        if status_influencer not in ["Pending","Accepted","Rejected"]:
            raise ValueError("Status must be 'Pending' or 'Accepted' or 'Rejected'")
        self.status_influencer=status_influencer
        
    def set_status_sponsor(self,status_sponsor):
        if status_sponsor not in ["Pending","Accepted","Rejected"]:
            raise ValueError("Status must be 'Pending' or 'Accepted' or 'Rejected'")
        self.status_sponsor=status_sponsor