from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask import current_app as app # Alias for current running app
from .models import *
from sqlalchemy import and_
from datetime import date, datetime


@app.route("/") # It refers base url 127.0.0.1:5000
def home():
    return render_template('index.html')


# Login  
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("user_name")
        pwd = request.form.get("password")  
        admin = Admin.query.filter_by(user_name=username).first()  # Use 'user_name' to match the model
        
        if admin and pwd == admin.password: 
            session['admin'] = username
            return redirect(url_for('admin_dashboard'))   
        else:
            flash("Wrong Username or Password")
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')  
# Login
@app.route("/login", methods=["GET", "POST"]) # It refers base url+/login
def login():
    if request.method == "POST":
        username = request.form.get("username")
        pwd = request.form.get("pwd")  
        user1 = Influencers.query.filter_by(username=username,flagged="NO").first()
        user2 = Sponsors.query.filter_by(username=username,flagged="NO").first()
        
        if user1:
            if pwd == user1.pwd:
                # Sets value in the session
                session['influencer'] = username
                return redirect(url_for('influencer_profile'))   
            else:
                flash("Wrong Username or Password")  
        elif user2:
            if pwd == user2.pwd: 
                session['sponsor'] = username
                return redirect(url_for('sponsor_profile'))   
            else:
                flash("Wrong Username or Password")   
        else:
            flash("User does not exist")
    return render_template("login.html")
# Logout
@app.route('/logout')
def logout():
    if 'influencer' in session or 'sponsor' in session:
        session.clear()
        flash('You have been logged out successfully.')
        return redirect(url_for('login'))
    elif 'admin' in session:
        session.clear()
        flash('You have been logged out successfully.')
        return redirect(url_for('home'))
    else:
        flash('No active session found.')
        return redirect(url_for('login'))  # Redirect to a default login page



# Add New Influencer
@app.route("/influencer", methods=["GET", "POST"])
def influencer():
    if request.method == "POST":
        username = request.form.get("username")
        name = request.form.get("name")
        email = request.form.get("email")
        niche = request.form.get("niche")
        platform = request.form.get("platform")
        followers = request.form.get("followers")
        pwd = request.form.get("pwd")
        # Validate input fields
        if not username or not name or not email or not pwd or not followers:
            flash("All fields are required.", "error")
            return redirect(url_for('sponsor'))
        if int(followers) <= 0:
            flash("Followers must be a whole number.")
            return redirect(url_for('campaign'))
        # Check if the username already exists
        existing_influencer = Influencers.query.filter_by(username=username,flagged="NO").first()
        existing_sponsor = Sponsors.query.filter_by(username=username,flagged="NO").first()
        if existing_influencer or existing_sponsor:
            flash("Username already taken, please choose another one.")
            return redirect(url_for('influencer'))
        
        new_influencer = Influencers(username=username, name=name, email=email,followers=followers, platform=platform, niche=niche, pwd=pwd) 

        db.session.add(new_influencer)
        db.session.commit() 
        flash("Influencer Added Successfully")      
        return redirect(url_for('influencer'))
    
    return render_template("influencer_signup.html")
   

# Edit Influencer 
@app.route("/influencer_profile/edit/<int:id>",methods=["POST"])
def edit_influencer(id):
    username = session.get('influencer')
    influencer = Influencers.query.filter_by(username=username,flagged="NO").first()

    if not username:
        flash("You must be logged in to view this page.")
        return redirect(url_for('login'))

    if not influencer:
        flash("No influencer found with that UserName.")
        return redirect(url_for('influencer'))
    id = influencer.id
    influencer = Influencers.query.get(id)
    
    influencer.name = request.form['name']
    influencer.username = request.form['username']
    influencer.email = request.form['email']
    influencer.niche = request.form['niche']
    influencer.platform = request.form['platform']
    influencer.followers = request.form['followers']

    db.session.commit()

    return redirect(url_for('influencer_profile'))

# Add New Sponsor
@app.route("/sponsor", methods=["GET", "POST"])
def sponsor():
    if request.method == "POST":
        username = request.form.get("username")
        name = request.form.get("name")
        email = request.form.get("email")
        industry = request.form.get("industry")
        pwd = request.form.get("pwd")
        budget = request.form.get("budget")
        # Validate input fields
        if not username or not name or not email or not pwd or not budget:
            flash("All fields are required.", "error")
            return redirect(url_for('sponsor'))
        if float(budget) <= 0:
            flash("Budget must be a positive number.")
            return redirect(url_for('campaign'))
        
    # Check if the username already exists
        existing_influencer = Influencers.query.filter_by(username=username,flagged="NO").first()
        existing_sponsor = Sponsors.query.filter_by(username=username,flagged="NO").first()
        if existing_influencer or existing_sponsor:
            flash("Username already taken, please choose another one.")
            return redirect(url_for('sponsor'))
        
        new_sponsor = Sponsors(username=username, name=name, email=email, industry=industry, budget=budget, pwd=pwd) 

        db.session.add(new_sponsor)
        db.session.commit() 
        flash("Sponsor Added Successfully")      
        return redirect(url_for('sponsor'))
    
    return render_template("sponsor_signup.html")

# Edit Sponsor 
@app.route("/sponsor_profile/edit/<int:id>",methods=["POST"])
def edit_sponsor(id):
    username = session.get('sponsor')
    sponsor = Sponsors.query.filter_by(username=username,flagged="NO").first()

    if not username:
        flash("You must be logged in to view this page.")
        return redirect(url_for('login'))

    if not sponsor:
        flash("No sponsor found with that UserName")
        return redirect(url_for('sponsor'))
    id = sponsor.id
    sponsor = Sponsors.query.get(id)
    
    sponsor.name = request.form['name']
    sponsor.username = request.form['username']
    sponsor.email = request.form['email']
    sponsor.industry = request.form['industry']
    sponsor.budget = request.form['budget']

    db.session.commit()

    return redirect(url_for('sponsor_profile'))

# Campaign Progress
def calculate_progress(start_date_str, end_date_str):
    date_format = "%Y-%m-%d"  # Format in which the date is stored
    start_date = datetime.strptime(start_date_str, date_format).date()
    end_date = datetime.strptime(end_date_str, date_format).date()
    today = date.today()

    total_duration = (end_date - start_date).days
    elapsed_duration = (today - start_date).days
    progress = (elapsed_duration / total_duration) * 100 if total_duration > 0 else 0
    return min(max(progress, 0), 100)  # Ensure progress is between 0 and 100

# View Sponsor Profile 
@app.route("/sponsor_profile")
def sponsor_profile():
    # session is a dictionary-like object used to store information about the current user across requests.
    # Retrieve the value(username) from the session 
    username=session.get('sponsor')
    if not username:
        flash("You must be login to view the page ")
        return redirect(url_for ('login'))
    username=session.get('sponsor')
    sponsor = Sponsors.query.filter_by(username=username,flagged="NO").first()
    if not sponsor:
        flash("No sponsor found with that UserName")
        return redirect(url_for('sponsor'))
    
    # Current Sponsor Id
    id = sponsor.id
    # Query to get campaigns for the current sponsor
    campaigns = Campaigns.query.filter_by(sponsor_id=id,flagged="NO").all()
    # Query to get ad requests for these campaigns
    ad_requests1 = Ad_requests.query.filter_by(status_influencer='Accepted',status_sponsor='Accepted').all()
    ad_requests2 = Ad_requests.query.filter_by(status_influencer='Accepted',status_sponsor='Pending').all()
    # Filtering campaigns to include only those with ad requests
    accepted_campaign_ids = {ad_request.campaign_id for ad_request in ad_requests1}
    pending_campaign_ids = {ad_request.campaign_id for ad_request in ad_requests2}

    active_campaigns = [campaign for campaign in campaigns if campaign.id in accepted_campaign_ids]
    pending_campaigns = [campaign for campaign in campaigns if campaign.id in pending_campaign_ids]
    # For Campaign Progress
    for campaign in active_campaigns:
        campaign.progress = calculate_progress(campaign.start_date, campaign.end_date)
    pending_campaign_ids_set = {campaign.id for campaign in pending_campaigns}
    # Another Query for ad_requests filter based on campaign_id and campaign with specific sponsor id
    ad_requests3 = Ad_requests.query.filter(Ad_requests.status_influencer == 'Accepted',Ad_requests.status_sponsor == 'Pending',Ad_requests.campaign_id.in_(pending_campaign_ids_set)).all()
    
    return render_template('sponsor_profile.html',sponsor=sponsor,ad_requests3=ad_requests3,active_campaigns=active_campaigns,pending_campaigns=pending_campaigns)

# View Influencer Profile
@app.route("/influencer_profile")
def influencer_profile():
    username = session.get('influencer')
    if not username:
        flash("You must be logged in to view this page.")
        return redirect(url_for('login'))

    influencer = Influencers.query.filter_by(username=username,flagged="NO").first()
    if not influencer:
        flash("No influencer found with that UserName.")
        return redirect(url_for('influencer'))
    # Current Influencer Id
    id = influencer.id
    
    # Query to get campaigns 
    campaigns = Campaigns.query.filter_by(flagged="NO").order_by(Campaigns.id).all()
    # Query to get ad requests for these campaigns
    ad_requests1 = Ad_requests.query.filter_by(status_influencer='Accepted',status_sponsor='Accepted',influencer_id=id).all()
    ad_requests2 = Ad_requests.query.filter_by(status_influencer='Pending',status_sponsor='Accepted',influencer_id=id).all()
    # Filtering campaigns to include only those with above ad requests
    accepted_campaign_ids = {ad_request.campaign_id for ad_request in ad_requests1}
    pending_campaign_ids = {ad_request.campaign_id for ad_request in ad_requests2}

    active_campaigns = [campaign for campaign in campaigns if campaign.id in accepted_campaign_ids]
    pending_campaigns = [campaign for campaign in campaigns if campaign.id in pending_campaign_ids]
    # For Campaign Progress
    for campaign in active_campaigns:
        campaign.progress = calculate_progress(campaign.start_date, campaign.end_date)
    pending_campaign_ids_set = {campaign.id for campaign in pending_campaigns}
    # Another Query for ad_requests filter based on campaign_id and campaign with specific sponsor id
    ad_requests3 = Ad_requests.query.filter(Ad_requests.status_influencer == 'Pending',Ad_requests.status_sponsor == 'Accepted',Ad_requests.campaign_id.in_(pending_campaign_ids_set)).all()
    
    return render_template('influencer_profile.html',influencer=influencer,active_campaigns=active_campaigns,pending_campaigns=pending_campaigns,ad_requests3=ad_requests3)

# Admin Dashboard
@app.route("/admin/dashboard")
def admin_dashboard():
    # Active entities
    campaigns = Campaigns.query.order_by(Campaigns.id).all()
    influencers = Influencers.query.order_by(Influencers.id).all()
    sponsors = Sponsors.query.order_by(Sponsors.id).all()

    ad_requests = Ad_requests.query.filter_by(status_influencer='Accepted', status_sponsor='Accepted').all()
    
    # Get all the campaign IDs from accepted ad requests
    accepted_campaign_ids = {ad_request.campaign_id for ad_request in ad_requests}
    
    # Get the influencer IDs involved in these accepted ad requests
    active_influencers_ids = {ad_request.influencer_id for ad_request in ad_requests}
    
    # Get the sponsor IDs from the campaigns associated with these accepted campaign IDs
    active_sponsors_ids = {campaign.sponsor_id for campaign in campaigns if campaign.id in accepted_campaign_ids}
    
    # Filter the active entities
    active_campaigns = [campaign for campaign in campaigns if campaign.id in accepted_campaign_ids]
    active_influencers = [influencer for influencer in influencers if influencer.id in active_influencers_ids]
    active_sponsors = [sponsor for sponsor in sponsors if sponsor.id in active_sponsors_ids]

    # For Campaign Progress
    for campaign in active_campaigns:
        campaign.progress = calculate_progress(campaign.start_date, campaign.end_date)

    # Flagged entities
    flagged_influencers = Influencers.query.filter_by(flagged="YES").all()
    flagged_sponsors = Sponsors.query.filter_by(flagged="YES").all()
    flagged_campaigns = Campaigns.query.filter_by(flagged="YES").all()

    return render_template('admin_dashboard.html', active_sponsors=active_sponsors, active_influencers=active_influencers, active_campaigns=active_campaigns,flagged_influencers=flagged_influencers,flagged_sponsors=flagged_sponsors,flagged_campaigns=flagged_campaigns)

@app.route("/admin/find", methods=["GET", "POST"]) 
def admin_find():
    if request.method == "POST":
        type_filter = request.form.get("type")
        niche_filter = request.form.get("niche")
        flagged_filter = request.form.get("flagged")

        influencers_query = Influencers.query
        campaigns_query = Campaigns.query
        sponsors_query = Sponsors.query

        # niche filter
        if niche_filter:
            influencers_query = influencers_query.filter(Influencers.niche == niche_filter)
            campaigns_query = campaigns_query.filter(Campaigns.niche == niche_filter)
            sponsors_query = sponsors_query.filter(Sponsors.industry == niche_filter)  # Assuming 'industry' in Sponsors is equivalent to 'niche'

        # flagged filter
        if flagged_filter:
            influencers_query = influencers_query.filter(Influencers.flagged == flagged_filter)
            campaigns_query = campaigns_query.filter(Campaigns.flagged == flagged_filter)
            sponsors_query = sponsors_query.filter(Sponsors.flagged == flagged_filter)

        # type filter
        influencers = influencers_query.all() if type_filter in ["Influencer", None, ""] else []
        campaigns = campaigns_query.all() if type_filter in ["Campaign", None, ""] else []
        sponsors = sponsors_query.all() if type_filter in ["Sponsor", None, ""] else []

    else:
        influencers = Influencers.query.order_by(Influencers.id).all()
        campaigns = Campaigns.query.order_by(Campaigns.id).all()
        sponsors = Sponsors.query.order_by(Sponsors.id).all()

    niches = ["Fashion", "Technology", "Travel", "Food", "Fitness", "Beauty", "Lifestyle", "Other"]
    flagged_options = ["YES", "NO"]

    return render_template("admin_find.html", influencers=influencers, campaigns=campaigns, sponsors=sponsors, niches=niches, flagged_options=flagged_options)





@app.route("/admin/campaign/<int:id>/flag", methods=["POST"])
def flag_campaign(id):

    campaign = Campaigns.query.get(id)
    
    if campaign.flagged == "YES":
        campaign.flagged = "NO"
        flash(f"Campaign '{campaign.title}' has been unflagged.", "success")
    else:
        campaign.flagged = "YES"
        flash(f"Campaign '{campaign.title}' has been flagged.", "success")
    
    db.session.commit()

    return redirect(url_for('admin_dashboard'))


@app.route("/admin/influencer/<int:id>/flag", methods=["POST"])
def flag_influencer(id):
    influencer = Influencers.query.get(id)

    if influencer.flagged == "YES":
        influencer.flagged = "NO"
        flash(f"Influencer '{influencer.username}' has been unflagged.", "success")
    else:
        influencer.flagged = "YES"
        flash(f"Influencer '{influencer.username}' has been flagged.", "success")
    
    db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/sponsor/<int:id>/flag", methods=["POST"])
def flag_sponsor(id):
    sponsor = Sponsors.query.get(id)
    
    if sponsor.flagged == "YES":
        sponsor.flagged = "NO"
        flash(f"Sponsor '{sponsor.username}' has been unflagged.", "success")
    else:
        sponsor.flagged = "YES"
        flash(f"Sponsor '{sponsor.username}' has been flagged.", "success")
    
    db.session.commit()
    
    return redirect(url_for('admin_dashboard'))


@app.route("/admin/stats")
def admin_stats():
    # Queries to fetch active and total entities
    campaigns = Campaigns.query.order_by(Campaigns.id).all()
    influencers = Influencers.query.order_by(Influencers.id).all()
    sponsors = Sponsors.query.order_by(Sponsors.id).all()

    ad_requests = Ad_requests.query.filter_by(status_influencer='Accepted', status_sponsor='Accepted').all()

    # Get all the campaign IDs from accepted ad requests
    accepted_campaign_ids = {ad_request.campaign_id for ad_request in ad_requests}
    active_influencers_ids = {ad_request.influencer_id for ad_request in ad_requests}
    active_sponsors_ids = {campaign.sponsor_id for campaign in campaigns if campaign.id in accepted_campaign_ids}

    # Filter the active entities
    active_campaigns = [campaign for campaign in campaigns if campaign.id in accepted_campaign_ids]
    active_influencers = [influencer for influencer in influencers if influencer.id in active_influencers_ids]
    active_sponsors = [sponsor for sponsor in sponsors if sponsor.id in active_sponsors_ids]

    # Total entities
    total_campaigns = len(campaigns)
    total_influencers = len(influencers)
    total_sponsors = len(sponsors)

    # Active entities
    active_campaigns_count = len(active_campaigns)
    active_influencers_count = len(active_influencers)
    active_sponsors_count = len(active_sponsors)

    # Flagged entities count
    flagged_influencers_count = len(Influencers.query.filter_by(flagged="YES").all())
    flagged_sponsors_count = len(Sponsors.query.filter_by(flagged="YES").all())
    flagged_campaigns_count = len(Campaigns.query.filter_by(flagged="YES").all())

    return render_template('admin_stats.html', 
                           total_campaigns=total_campaigns, 
                           total_influencers=total_influencers, 
                           total_sponsors=total_sponsors,
                           flagged_influencers_count=flagged_influencers_count,
                           flagged_sponsors_count=flagged_sponsors_count,
                           flagged_campaigns_count=flagged_campaigns_count,
                           active_sponsors=active_sponsors_count,
                           active_influencers=active_influencers_count,
                           active_campaigns=active_campaigns_count)



# View Campaign Sponsor
@app.route("/sponsor/campaign/view/<int:id>")
def campaignSp_view(id):
    username=session.get('sponsor')
    sponsor = Sponsors.query.filter_by(username=username).first()# For Navbar

    campaign = Campaigns.query.filter_by(id=id,flagged="NO").first()
    id = campaign.id
    ad_requests=Ad_requests.query.filter_by(campaign_id=id).all()
    return render_template('campaign_view.html',ad_requests=ad_requests,campaign=campaign,sponsor=sponsor)


# View Campaign Influencer
@app.route("/influencer/campaign/view/<int:id>")
def campaignIn_view(id):
    username=session.get('influencer')
    influencer = Influencers.query.filter_by(username=username).first()# For Navbar
    campaign = Campaigns.query.filter_by(id=id,flagged="NO").first()
    id = campaign.id
    ad_requests=Ad_requests.query.filter_by(campaign_id=id).all()
    return render_template('campaign_view.html',ad_requests=ad_requests,campaign=campaign,influencer=influencer)
    
# View Campaign Sponsor 
@app.route("/campaigns") 
def campaigns():
    username=session.get('sponsor')
    sponsor=Sponsors.query.filter_by(username=username).first()
    campaigns=Campaigns.query.filter_by(flagged="NO").order_by(Campaigns.sponsor_id).all()
    return render_template('campaigns.html',sponsor=sponsor,campaigns=campaigns)

# # Sponsor Side 
# Accept Request 
@app.route("/accept_request/<int:id>")
def accept_request(id):
    username = session.get('sponsor')
    if not username:
        flash("You must be logged in to perform this action.")
        return redirect(url_for('login'))

    sponsor = Sponsors.query.filter_by(username=username).first()
    if not sponsor:
        flash("No sponsor found with that UserName.")
        return redirect(url_for('sponsor'))

    ad_request = Ad_requests.query.get(id)
    if not ad_request:
        flash("Ad request not found.")
        return redirect(url_for('sponsor_profile'))

    ad_request.status_sponsor = 'Accepted'
    db.session.commit() 

    flash("Ad request accepted successfully.")
    return redirect(url_for('sponsor_profile'))

# Reject Request
@app.route("/reject_request/<int:id>")
def reject_request(id):
    username = session.get('sponsor')
    if not username:
        flash("You must be logged in to perform this action.")
        return redirect(url_for('login'))

    sponsor = Sponsors.query.filter_by(username=username).first()
    if not sponsor:
        flash("No sponsor found with that UserName.")
        return redirect(url_for('sponsor'))

    ad_request = Ad_requests.query.get(id)
    if not ad_request:
        flash("Ad request not found.")
        return redirect(url_for('sponsor_profile'))

    ad_request.status_sponsor = 'Rejected'
    db.session.commit() 

    flash("Ad request rejected successfully.")
    return redirect(url_for('sponsor_profile'))

# Delete Request
@app.route("/delete_request/<int:id>", methods=["POST"])
def delete_request(id):
    username = session.get('sponsor')
    if not username:
        flash("You must be logged in to perform this action.")
        return redirect(url_for('login'))

    sponsor = Sponsors.query.filter_by(username=username).first()
    if not sponsor:
        flash("No sponsor found with that UserName.")
        return redirect(url_for('sponsor'))

    ad_request = Ad_requests.query.get(id)
    if not ad_request:
        flash("Ad request not found.")
        return redirect(url_for('sponsor_profile'))

    db.session.delete(ad_request)
    db.session.commit()  

    flash("Ad request deleted successfully.")
    return redirect(url_for('sponsor_profile'))

# Edit Request 
@app.route("/edit_request/<int:id>", methods=["POST"])
def edit_request(id):

    ad_request = Ad_requests.query.get(id)
    
    ad_request.name = request.form['name']
    ad_request.message = request.form['message']
    ad_request.requirements = request.form['requirements']
    ad_request.payment_amount = request.form['payment_amount']
    ad_request.status_sponsor = request.form['status_sponsor']

    db.session.commit()
    flash("AD Request Edited Successfully")
    return redirect(url_for('campaignSp_view',id=ad_request.campaign_id))

# # Influencer
# Accept Request
@app.route("/accept_request_in/<int:id>")
def accept_request_in(id):
    username = session.get('influencer')
    if not username:
        flash("You must be logged in to perform this action.")
        return redirect(url_for('login'))

    influencer = Influencers.query.filter_by(username=username).first()
    if not influencer:
        flash("No sponsor found with that UserName.")
        return redirect(url_for('influencer'))

    ad_request = Ad_requests.query.get(id)
    if not ad_request:
        flash("Ad request not found.")
        return redirect(url_for('influencer_profile'))

    ad_request.status_influencer = 'Accepted'
    db.session.commit()  # Save changes to the database

    flash("Ad request accepted successfully.")
    return redirect(url_for('influencer_profile'))
# Reject Request
@app.route("/reject_request_in/<int:id>")
def reject_request_in(id):
    username = session.get('sponsor')
    if not username:
        flash("You must be logged in to perform this action.")
        return redirect(url_for('login'))

    ad_request = Ad_requests.query.get(id)
    if not ad_request:
        flash("Ad request not found.")
        return redirect(url_for('influencer_profile'))

    ad_request.status_influencer = 'Rejected'
    db.session.commit()  # Save changes to the database

    flash("Ad request rejected successfully.")
    return redirect(url_for('influencer_profile'))

# Create a Campaign
@app.route("/campaign", methods=['GET', 'POST'])
def campaign():
    username = session.get('sponsor')
    sponsor = Sponsors.query.filter_by(username=username).first()

    if not sponsor:
        flash("Session Expired")
        return redirect(url_for('login'))

    if request.method == "POST":
        # Retrieve form data
        title = request.form.get("title")
        description = request.form.get("description")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        visibility = request.form.get("visibility")
        budget = request.form.get("budget")
        goal = request.form.get("goal")
        niche = request.form.get("niche")

        # Validation
        if not title or not description or not start_date or not end_date or not budget or not goal or not niche or not visibility:
            flash("All fields are required.")
            return redirect(url_for('campaign'))

        if end_date < start_date:
            flash("End Date cannot be before Start Date.")
            return redirect(url_for('campaign'))

        if float(budget) <= 0:
            flash("Budget must be a positive number.")
            return redirect(url_for('campaign'))

        # Add the new campaign to the database
        new_campaign = Campaigns(description=description,title=title,start_date=start_date,end_date=end_date,niche=niche,goal=goal,visibility=visibility,budget=budget,sponsor_id=sponsor.id)

        db.session.add(new_campaign)
        db.session.commit()
        flash("Campaign Added Successfully")
        return redirect(url_for('campaign'))

    return render_template('campaign.html', sponsor=sponsor)


# Edit a Campaign
@app.route("/edit_campaign/<int:id>", methods=["POST"])
def edit_campaign(id):
    campaign = Campaigns.query.get(id)
    if campaign.flagged=="NO":
        campaign.title = request.form['title']
        campaign.description = request.form['description']
        campaign.budget = request.form['budget']
        campaign.start_date = request.form['start_date']
        campaign.end_date = request.form['end_date']
        campaign.visibility = request.form['visibility']
        campaign.goal = request.form['goal']
        campaign.niche = request.form['niche']

        db.session.commit()
        flash("Campaign Edited Successfully")
        return redirect(url_for('campaigns'))
    else:
        flash("This Campaign has been flagged by the admin")
        return redirect (url_for(campaignSp_view))
        
# Delete a Campaign
@app.route("/delete_campaign/<int:id>", methods=["POST"])
def delete_campaign(id):
    campaign = Campaigns.query.get(id)
    Ad_requests.query.filter_by(campaign_id=id).delete()

    db.session.delete(campaign)
    db.session.commit()
    
    flash("Campaign Deleted Successfully")
    return redirect(url_for('campaigns'))

# Create a ad request from Sponsor side
@app.route("/sponsor/request/<int:id>", methods=['GET', 'POST'])
def sponsor_request(id):
    username = session.get('sponsor')  # Fetch the sponsor username from the session
    sponsor = Sponsors.query.filter_by(username=username).first()
    
    if request.method == "POST":
        name = request.form.get("name")
        message = request.form.get("message")
        requirements = request.form.get("requirements")
        payment_amount = request.form.get("payment_amount")
        status = "Accepted"
        find_inf_id = request.form.get("id")

        # Validation
        if not name or not find_inf_id or not requirements or not payment_amount:
            flash("All fields are required", "error")
            return redirect(url_for('sponsor_request', id=id))
        
        if not payment_amount.isdigit() or int(payment_amount) <= 0:
            flash("Payment amount must be a positive number", "error")
            return redirect(url_for('sponsor_request', id=id))
        
        # Create ad request
        ad_request = Ad_requests(influencer_id=find_inf_id, campaign_id=id, name=name, message=message, requirements=requirements, payment_amount=payment_amount, status_sponsor=status)
        
        db.session.add(ad_request)
        db.session.commit()
        flash("Request Sent Successfully")
        return redirect(url_for('sponsor_request', id=id))
    
    return render_template('ad_request.html', sponsor=sponsor, id=id)


# Create a ad request from Influencer side
@app.route("/influencer/request/<int:id>", methods=['GET', 'POST'])
def influencer_request(id):
    username = session.get('influencer')  # Fetch the influencer username from the session
    influencer = Influencers.query.filter_by(username=username).first()
    
    if request.method == "POST":
        name = request.form.get("name")
        message = request.form.get("message")
        requirements = request.form.get("requirements")
        payment_amount = request.form.get("payment_amount")
        status = "Accepted"
        # Validation
        if not name or not requirements or not payment_amount:
            flash("All fields are required", "error")
            return redirect(url_for('sponsor_request', id=id))
        
        if not payment_amount.isdigit() or int(payment_amount) <= 0:
            flash("Payment amount must be a positive number", "error")
            return redirect(url_for('sponsor_request', id=id))
        ad_request = Ad_requests(influencer_id=influencer.id,campaign_id=id,name=name,message=message,requirements=requirements,payment_amount=payment_amount,status_influencer=status)
        
        db.session.add(ad_request)
        db.session.commit()
        flash("Request Sent Successfully")
        return redirect(url_for('influencer_request', id=id))
    
    return render_template('ad_request.html', influencer=influencer,id=id)

#   Sponsors Find Page
@app.route("/sponsor/find", methods=["GET", "POST"]) 
def sponsor_find():
    username = session.get('sponsor')
    sponsor = Sponsors.query.filter_by(username=username).first() # For Navbar 

    if request.method == "POST":
        search_query = request.form.get("search")
        niche_filter = request.form.get("niche")
        platform_filter = request.form.get("platform")

        influencers_query = Influencers.query.filter_by(flagged="NO")
        campaigns_query = Campaigns.query.filter_by(flagged="NO")

        if search_query:
            influencers_query = influencers_query.filter(
                Influencers.flagged == "NO" ,
                Influencers.name.ilike(f"%{search_query}%") |
                Influencers.username.ilike(f"%{search_query}%") |
                Influencers.niche.ilike(f"%{search_query}%") |
                Influencers.platform.ilike(f"%{search_query}%")
            )
            campaigns_query = campaigns_query.filter(
                Campaigns.flagged == "NO",
                Campaigns.title.ilike(f"%{search_query}%") |
                Campaigns.description.ilike(f"%{search_query}%") |
                Campaigns.niche.ilike(f"%{search_query}%")
            )

        if niche_filter:
            influencers_query = influencers_query.filter(Influencers.niche == niche_filter,Influencers.flagged=="NO")
            campaigns_query = campaigns_query.filter(Campaigns.niche == niche_filter,Campaigns.flagged=="NO")

        if platform_filter:
            influencers_query = influencers_query.filter(Influencers.platform == platform_filter,Influencers.flagged=="NO")

        influencers = influencers_query.all()
        campaigns = campaigns_query.all()
    else:
        influencers = Influencers.query.filter_by(flagged="NO").order_by(Influencers.id).all()
        campaigns = Campaigns.query.filter_by(visibility="Public",flagged="NO").order_by(Campaigns.id).all()

    niches = ["Fashion", "Technology", "Travel", "Food", "Fitness", "Beauty", "Lifestyle", "Other"]
    platforms = ["Youtube", "Instagram", "Twitter", "Other"]

    return render_template("sponsor_find.html", sponsor=sponsor, influencers=influencers, campaigns=campaigns, niches=niches, platforms=platforms)

# Influencer Find Page
@app.route("/influencer/find", methods=["GET", "POST"]) 
def influencer_find():
    username = session.get('influencer')
    influencer = Influencers.query.filter_by(username=username).first() # For Navbar 

    if request.method == "POST":
        search_query = request.form.get("search")
        niche_filter = request.form.get("niche")
        campaigns = Campaigns.query.filter(
            Campaigns.visibility == "Public",
            Campaigns.flagged == "NO",
            Campaigns.title.ilike(f"%{search_query}%") |
            Campaigns.description.ilike(f"%{search_query}%") |
            Campaigns.niche.ilike(f"%{search_query}%")
        ).all()

        if niche_filter:
            campaigns = [campaign for campaign in campaigns if campaign.niche == niche_filter]
    else:
        campaigns = Campaigns.query.filter_by(visibility="Public",flagged="NO").order_by(Campaigns.id).all()

    niches = ["Fashion", "Technology", "Travel", "Food", "Fitness", "Beauty", "Lifestyle", "Other"]
    return render_template('influencer_find.html', influencer=influencer, campaigns=campaigns, niches=niches)

# Sponsor Stats
@app.route("/sponsor_stats")
def sponsor_stats():
    username = session.get('sponsor')
    if not username:
        flash("You must be logged in to view this page.")
        return redirect(url_for('login'))

    sponsor = Sponsors.query.filter_by(username=username).first()
    if not sponsor:
        flash("No sponsor found with that username.")
        return redirect(url_for('sponsor'))

    # Current Sponsor Id
    sponsor_id = sponsor.id
    
    # Query to get campaigns for the current sponsor
    campaigns = Campaigns.query.filter_by(sponsor_id=sponsor_id).all()
    campaign_ids_set = {campaign.id for campaign in campaigns}
    
    # Query to get ad requests for campaigns based on statuses
    ad_requests = Ad_requests.query.filter(Ad_requests.campaign_id.in_(campaign_ids_set)).all()

    # Separate ad requests based on status combinations
    accepted_by_both = [ad for ad in ad_requests if ad.status_influencer == 'Accepted' and ad.status_sponsor == 'Accepted']
    pending_ads = [ad for ad in ad_requests if ad.status_influencer == 'Pending' or ad.status_sponsor == 'Pending']
    # We didn't used it
    accepted_by_influencer = [ad for ad in ad_requests if ad.status_influencer == 'Accepted' and ad.status_sponsor == 'Pending']
    
    # Calculate totals
    total_ads = len(ad_requests)
    total_accepted = len(accepted_by_both)
    total_pending = len(pending_ads)
    
    # Prepare data for campaign performance
    campaign_names = [campaign.title for campaign in campaigns]
    
    total_ads_per_campaign = [
        len([ad for ad in ad_requests if ad.campaign_id == campaign.id])
        for campaign in campaigns
    ]
    
    accepted_ads_per_campaign = [
        len([ad for ad in accepted_by_both if ad.campaign_id == campaign.id])
        for campaign in campaigns
    ]
    
    pending_ads_per_campaign = [
        len([ad for ad in pending_ads if ad.campaign_id == campaign.id])
        for campaign in campaigns
    ]
    
    return render_template(
        'sponsor_stats.html',
        sponsor=sponsor,
        total_ads=total_ads,
        total_accepted=total_accepted,
        total_pending=total_pending,
        campaign_names=campaign_names,
        total_ads_per_campaign=total_ads_per_campaign,
        accepted_ads_per_campaign=accepted_ads_per_campaign,
        pending_ads_per_campaign=pending_ads_per_campaign
    )





# Influencer Stats
@app.route("/influencer_stats")
def influencer_stats():
    username = session.get('influencer')
    if not username:
        flash("You must be logged in to view this page.")
        return redirect(url_for('login'))

    influencer = Influencers.query.filter_by(username=username).first()
    if not influencer:
        flash("No influencer found with that username.")
        return redirect(url_for('influencer'))
    
    # Current Influencer Id
    influencer_id = influencer.id

    # Query to get ad requests for the current influencer
    ad_requests = Ad_requests.query.filter_by(influencer_id=influencer_id).all()

    # Separate ad requests based on status combinations
    accepted_by_both = [ad for ad in ad_requests if ad.status_influencer == 'Accepted' and ad.status_sponsor == 'Accepted']
    pending_ads = [ad for ad in ad_requests if ad.status_influencer == 'Pending' or ad.status_sponsor == 'Pending']

    # Calculate totals
    total_campaigns = len(ad_requests)
    total_accepted = len(accepted_by_both)
    total_pending = len(pending_ads)
    
    # Calculate acceptance rate
    acceptance_rate = (total_accepted / total_campaigns) * 100 if total_campaigns > 0 else 0

    # Prepare data for campaign performance
    campaigns_stats = {}
    for ad_request in ad_requests:
        campaign_id = ad_request.campaign_id
        if campaign_id not in campaigns_stats:
            campaigns_stats[campaign_id] = {
                'name': ad_request.campaign.title,
                'total_ads': 0,
                'accepted_ads': 0,
                'pending_ads': 0
            }
        campaigns_stats[campaign_id]['total_ads'] += 1
        if ad_request.status_influencer == 'Accepted':
            campaigns_stats[campaign_id]['accepted_ads'] += 1
        elif ad_request.status_influencer == 'Pending':
            campaigns_stats[campaign_id]['pending_ads'] += 1

    # Data for charts
    campaign_names = [stats['name'] for stats in campaigns_stats.values()]
    total_ads = [stats['total_ads'] for stats in campaigns_stats.values()]
    accepted_ads = [stats['accepted_ads'] for stats in campaigns_stats.values()]
    pending_ads = [stats['pending_ads'] for stats in campaigns_stats.values()]

    return render_template('influencer_stats.html', 
                           influencer=influencer, 
                           total_campaigns=total_campaigns, 
                           total_accepted=total_accepted, 
                           total_pending=total_pending,
                           acceptance_rate=acceptance_rate,
                           campaign_names=campaign_names,
                           total_ads=total_ads,
                           accepted_ads=accepted_ads,
                           pending_ads=pending_ads)
