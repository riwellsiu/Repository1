##Here we import all of the necessary tools to build the website###
from flask import Flask #The FLASK framework (the webserver)
from flask import render_template  # For opening and read the HTML file and showing them as the webpage
from flask import request  #Allows me to get stuff from the URL (the ?)
from flask import redirect, url_for, flash, session
import sqlite3
from flask import redirect, url_for # Use images from the static folder
from classes.databaseclasses import *
##Creating the key for the website login##
app=Flask(__name__)
app.secret_key = 'beluga'
##Route for the login page##
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['hashedPassword']
##make sure they submit##
        if not username or not password:
            flash('Username and password are required', 'error')
            return redirect(url_for('login'))

        conn = sqlite3.connect('mainframe.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE email=?", (username,))
        user = cursor.fetchone()
        conn.close()
        errorList = validateLoginForm(request.form)
        ##validate the inputs##
        if user is None or user[4] != password:
            flash('Invalid username or password', 'error')
        elif len(errorList) > 0: #Send the form to the validation
            return render_template('login.html', message = errorList)
        else:
            session['user_id'] = user[0]
            # flash('Login successful', 'success')
            #changed
##creating the session
            user_id = session.get('user_id')
            user1.updatelastloginDB(user_id)
            #edn cnage
            return redirect(url_for('profile'))

    return render_template('login.html')
##this creates the landing page from the login###
@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if user_id is None:
        flash('Please log in to access your profile', 'error')
        return redirect(url_for('login'))
##connecting to database to retrieve all of the applicable data##
    conn = sqlite3.connect('mainframe.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE userid=?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    type = user["type"]
##creating admin priveleges##
    if user["type"] == "admin":
        category = '<button type="button">View Categories</button>'

    else:
        category=""

    user_name = user['email']
    mlist = user1.getSingleUserList_DB(user_id)
    bestpeople = user1.getbestusers()
    threelistings= listing.getNewestListings()
    # Add your profile page content here
    return render_template('profile.html', user_name = user_name, user_id = user_id, message = mlist, category = category, type = type,message2 = bestpeople, message3=threelistings)
##setting up the logout page##
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

##editing profile page##
@app.route('/editprofile', methods=['GET', 'POST'])
def EditFUNCTION():
    if request.method == "GET":
        # GET The user id
        user_id = session.get('user_id')
        mSingleDict = user1.getSingleUserList_DB(user_id)
        # PASS THE SINGLE user TO THE editprof.html PAGE
        return render_template('editprof.html',message=mSingleDict )
    elif request.method == "POST":
        fName     = request.form.get("firstName"     , 0)
        lName     = request.form.get("lastName"     , 0)
        email  = request.form.get("email"  , 0)
        psswd = request.form.get("hashedPassword" , 0)
        image   = request.form.get("profileImage"   , 0)
        location  = request.form.get("location"   , 0)
        errorList = validateEditForm(request.form)  #Send the form to the validation
        if len(errorList) > 0:
            return render_template('editprof.html', message = errorList)
        else: # Form passed the validation
            user_id = session.get('user_id')
            user1.updateprofileDB(user_id,fName,
                                lName,
                                email,
                                psswd,
                                image,
                                location)
            profiletoshow = user1.getSingleUserList_DB(user_id)
            return render_template('editprof.html',message=profiletoshow)
##app route to add a profile into the database
@app.route("/addprofile", methods=["GET","POST"]) # Decorator - Now
def add():
    if request.method == "GET":  # When you first visit the page
        return render_template('insertaccount.html')
    elif request.method == "POST": # When you fill out the form and click SUBMIT
        fName     = request.form.get("firstName"     , 0)
        lName     = request.form.get("lastName"     , 0)
        email  = request.form.get("email"  , 0)
        psswd = request.form.get("hashedPassword" , 0)
        image   = request.form.get("profileImage"   , 0)
        location  = request.form.get("location"   , 0)
        errorList = validateAddForm(request.form)  #Send the form to the validation
        #if email in emaillist:
            #return render_template('insertaccount.html', message1 = "this email is already taken")
        if len(errorList) > 0:
            return render_template('insertaccount.html', message1 = errorList)
        else: # Form passed the validation
            user1.saveauser(fName,
                                lName,
                                email,
                                psswd,
                                image,
                                location)
            return render_template('login.html')
#### SERVER SIDE VALIDATION BEGINS###

###Here is the edit user validation
def validateAddForm(form):
    tmpList = []
    emaillist = user1.getAllemails()
    fName     = request.form.get("firstName"     , 0)
    lName     = request.form.get("lastName"     , 0)
    email  = request.form.get("email"  , 0)
    psswd = request.form.get("hashedPassword" , 0)
    image   = request.form.get("profileImage"   , 0)
    location  = request.form.get("location"   , 0)
    imagefile = [".jpg", ".png"]
    ##making a list of errors if the form is invalid##
    if fName is None or len(fName) < 2:
        tmpList.append({"Error" : "First Name must be at least 2 characters."})
    if lName is None or len(lName) < 2:
        tmpList.append({"Error" : "Last Name must be at least 2 characters."})
    if email is None or '@' not in email:
        tmpList.append({"Error" : "email must contain an @ sign"})
    if email in emaillist:
        tmpList.append({"Error" : "email must be unique"})
    if psswd is None or len(psswd) < 8:
        tmpList.append({"Error" : "Password needs 8 characters."})
    if image is None:
        tmpList.append({"Error" : "Image cannot be blank."})
    if image[-4:] not in imagefile:
        tmpList.append({"Error" : "Image format is incorrect. Provide .jpg or .png."})
    if location is None or len(location) < 2:
        tmpList.append({"Error" : "Location must be at least 2 characters."})
    return tmpList

def validateEditForm(form):
    tmpList = []
    fName     = request.form.get("firstName"     , 0)
    lName     = request.form.get("lastName"     , 0)
    email  = request.form.get("email"  , 0)
    psswd = request.form.get("hashedPassword" , 0)
    image   = request.form.get("profileImage"   , 0)
    location  = request.form.get("location"   , 0)
    imagefile = [".jpg", ".png"]
    ##making a list of errors if the form is invalid##
    if fName is None or len(fName) < 2:
        tmpList.append({"Error" : "First Name must be at least 2 characters."})
    if lName is None or len(lName) < 2:
        tmpList.append({"Error" : "Last Name must be at least 2 characters."})
    if email is None or '@' not in email:
        tmpList.append({"Error" : "email must contain an @ sign"})
    if psswd is None or len(psswd) < 8:
        tmpList.append({"Error" : "Password needs 8 characters."})
    if image is None:
        tmpList.append({"Error" : "Image cannot be blank."})
    if image[-4:] not in imagefile:
        tmpList.append({"Error" : "Image format is incorrect. Provide .jpg or .png."})
    if location is None or len(location) < 2:
        tmpList.append({"Error" : "Location must be at least 2 characters."})
    return tmpList

def validateLoginForm(form):
    tmpList = []
    username = request.form.get("email"     , 0)
    password = request.form.get("hashedPassword"     , 0)
    special_characters = ["<", ">", "%", "#"]
    ##making a list of errors if the form is invalid##
    for char in special_characters:
        if char in username:
            tmpList.append({"Error" : "Username cannot have special characters."})
    if password is None:
        tmpList.append({"Error" : "Password cannot be empty."})
    return tmpList

def validateEDITreview(form):
    tmpList = []
    comment = request.form.get("description", 0)
    special_characters = ["<", ">", "%", "#"]
    ##making a list of errors if the form is invalid##
    for char in special_characters:
        if char in comment:
            tmpList.append({"Error" : "cannot have special characters."})
    if len(comment) <20 or len(comment) > 1000:
        tmpList.append({"Error" : "Comment should be between 20-1000 chars."})
    return tmpList

def validateNEWreview(form):
    tmpList = []
    email = request.form.get("email", 0)
    comment = request.form.get("description", 0)
    special_characters = ["<", ">", "%", "#"]
    reviewedusersid = user1.getsingleuserid(email)
    currentusersid = session.get('user_id')
    ##making a list of errors if the form is invalid##
    if reviewedusersid == currentusersid:
        tmpList.append({"Error" : "You cannot review yourself."})
    for char in special_characters:
        if char in comment:
            tmpList.append({"Error" : "cannot have special characters."})
    if len(comment) <20 or len(comment) > 1000:
        tmpList.append({"Error" : "Comment should be between 20-1000 chars."})
    return tmpList

def validateNewListingForm(form):
    tmpList = []
    title = request.form.get("title"     , 0)
    title = title.strip()
    description = request.form.get("description"     , 0)
    description = description.strip()
    image = request.form.get("image"     , 0)
    image = image.strip()
    category = request.form.get("category"     , 0)
    category = category.strip()
    catlist = Category.getAllCategories2()
    special_characters = ["<", ">", "%", "#"]
    imagefile = [".jpg", ".png"]
    ##making a list of errors if the form is invalid##
    for char in special_characters:
        if char in title:
            tmpList.append({"Error" : "Title cannot have special characters."})
    if len(title) < 10 or len(title) > 100:
        tmpList.append({"Error" : "Title must be between 10 and 100 characters."})
    if title is None:
        tmpList.append({"Error" : "title cannot be empty."})
    for char in special_characters:
        if char in description:
            tmpList.append({"Error" : "Description cannot have special characters."})
    if len(description) < 20 or len(description) > 2000:
        tmpList.append({"Error" : "Description must be between 20 and 2000 characters."})
    if description is None:
        tmpList.append({"Error" : "Description cannot be empty."})
    if category not in catlist:
        tmpList.append({"Error" : "Category must be selected."})
    if category is None:
        tmpList.append({"Error" : "Category is empty."})
    if image[-4:] not in imagefile:
        tmpList.append({"Error" : "Image format is incorrect. Provide .jpg or .png."})
    return tmpList

#### SERVER SIDE VALIDATION ENDS###
##app route to view all of the listings##
@app.route("/listings", methods=["GET"])
def view():
    if request.method == "GET":  # When you first visit the page

        listings=listing.getAllListings()
        categories = Category.getAllCategories()
        return render_template('listings.html',message=listings, categories=categories)
        #in the case of no listings
    else:
        return render_template('addlisting.html',message='There are no listings.')
@app.route("/listings", methods=["POST"])
def viewfilter():
    if request.method == "POST":  # When you click on the button
        category = request.form.get("category", 0)
        listings=listing.getfilteredListings(category)
        categories = Category.getAllCategories()
        return render_template('listings.html',message=listings, categories=categories)
#takes you to the add listing page if there are none##
    else:
        return render_template('addlisting.html',message='There are no listings.')

##chance to add a listing
@app.route("/addlisting", methods=["GET","POST"])
def addListing():
    if request.method == "GET":
        categories=Category.getAllCategories()
        return render_template('addlisting.html', categories=categories)
##once you hit sumbit##
    elif request.method == "POST":
        userID = session.get('user_id')
        title = request.form.get("title", 0)
        description = request.form.get("description", 0)
        image = request.form.get("image", 0)
        category = request.form.get("category", 0)
        errorList = validateNewListingForm(request.form)  #Send the form to the validation
        if len(errorList) > 0:
            return render_template('addlisting.html', message1 = errorList)
##this is when the listing looks good based on validation
        else:
            listing.addListing(userID, title, description, image, category)
            userID = session.get('user_id')
            viewListing=listing.myListing(userID)
            message2 = "Your listing was successfully added"
        return render_template("mylistings.html", message = viewListing, message2 = message2)
#viewing a listing based on the listing id
@app.route("/viewListing/<int:listingID>", methods=["GET"])
def viewListing(listingID):
    viewListing=listing.getListing(listingID)
    usersID = listing.getsingleuseridfromlistid(listingID)
    ##calculating the average of that users review
    rating = review.reviewaverage(usersID)
    return render_template("viewlisting.html",message=viewListing, message2 = rating )
#deleting a listing based on its id##
@app.route("/deleteListing/<int:listingID>", methods=['POST', 'DELETE', 'GET'])
def deleteListing(listingID):

    listing.deleteListing(listingID)
    userID = session.get("user_id")
    listings=listing.myListing(userID)

    return render_template("mylistings.html",message=listings)
##editing a listings
@app.route("/editListing/<int:listingID>", methods=['POST', 'GET'])
def editListing(listingID):
    if request.method == "GET":

        categories = Category.getAllCategories()
#pulling the listing based on its id##
        viewListing=listing.getListing(listingID)

        return render_template("editlisting.html",listings=viewListing, categories=categories )
##when hitting the submit button we pull data##
    elif request.method == "POST":
        listingID = request.form.get("id", 0)
        title = request.form.get("title", 0)
        description = request.form.get("description", 0)
        category = request.form.get("category", 0)
        image = request.form.get("image", 0)
        status = request.form.get("status", 0)

        listing.updateListing(listingID, title, description, image, category, status)

        return redirect("/mylisting")
##this shows me all of the listings I have made##
@app.route("/mylisting", methods=["GET"])
def myListing():
    userID = session.get('user_id')
    viewListing=listing.myListing(userID)

    return render_template("mylistings.html", message=viewListing )

## when i want to see a specific one of my listings##
@app.route("/viewMyListing/<int:listingID>", methods=["GET"])
def viewMyListing(listingID):
    viewListing=listing.getListing(listingID)

    return render_template("viewMyListing.html",message=viewListing )

##when the admin wants to view all of the categories##
@app.route("/categories", methods=["GET"])
def viewCategories():
    if request.method == "GET":  # When you first visit the page

        categories=Category.getAllCategories()
        return render_template('categories.html', categories=categories)
    else:
        return render_template('addcategory.html',message='There are no listings.')
##chance to view a specific category to get more details##
@app.route("/viewCategory/<int:categoryID>", methods=["GET"])
def viewCategory(categoryID):

    viewCategory=Category.viewCategory(categoryID)

    return render_template("viewcategory.html",message=viewCategory )
##editing the category if necessary - only available to admins##
@app.route("/editCategory/<int:categoryID>", methods=['POST', 'GET'])
def editCategory(categoryID):
    if request.method == "GET":

        categories = Category.viewCategory(categoryID)

        return render_template("editcategory.html",categories=categories )
##retrieving the data from the form##
    elif request.method == "POST":
        categoryID = request.form.get("id", 0)
        name = request.form.get("name", 0)
        description = request.form.get("description", 0)

        Category.updateCategory(categoryID, name, description)
        return redirect("/categories")

##deleting a specific category
@app.route("/deleteCategory/<int:categoryID>", methods=['POST', 'DELETE', 'GET'])
def deleteCategory(categoryID):

    Category.deleteCategory(categoryID)

    return redirect("/categories")
#adding a category base space for the admin
@app.route("/addcategory")
def addCategoryPage():
    return render_template("addcategory.html")
##when they post, collect items from the form and save to database
@app.route("/addCategory", methods=["POST"])
def addCategory():
    if request.method == "POST":
        name = request.form.get("name", 0)
        description = request.form.get("description", 0)
        Category.addCategory(name, description)
        return redirect("/categories")
##adding a review page for the user, collect all emails from thedatabase
@app.route("/addReview",methods=["GET"])
def addRevPage():
    userlist = user1.getAllusers()
    return render_template("newreview.html", message = userlist)
##ability to add a review once the details are filled out
@app.route("/addReview",methods=["POST"])
def submitreviewPage():
    reviewerid = session.get('user_id')
    revieweduser = request.form.get("email", 0)
    rating = request.form.get("rating", 0)
    reviewedpersonsid = user1.getuserIDfromemail(revieweduser)
    comment = request.form.get("description", 0)
    errorList = validateNEWreview(request.form)
    if len(errorList) > 0:
            messageofrev = user1.getAllusers()
            return render_template('newreview.html', message1 = errorList, message = messageofrev)
            #at this point if this does nottrigger, the form is valid
    else:
        review.addReview(reviewerid,reviewedpersonsid,rating,comment)
        reviewlist = review.getAllReviews()
        return render_template("allreviews.html", message = reviewlist)
##way to see all of the reviews sitting inside of the database, pull all users to get the ability to filter
@app.route("/allReviews",methods=["GET"])
def viewallreviews():
    userlist = user1.getAllusers()
    reviewlist = review.getAllReviews()
    return render_template("allreviews.html", message = reviewlist, message2 = userlist)
## saving all of the data from the form##
@app.route("/allReviews",methods=["POST"])
def filteredreviews():
    reviewedIDemail = request.form.get("email", 0)
    reviewID = review.filterreviews(reviewedIDemail)
    listofreviews = review.getAllReviewsSinglePerson(reviewID)
    userlist = user1.getAllusers()
    return render_template("allreviews.html", message = listofreviews, message2 = userlist)




##view a review by the review id##

@app.route("/viewReview/<int:reviewID>",methods=["GET"])
def viewReview(reviewID):
    messageofrev = review.viewreview(reviewID)
    return render_template("viewreview.html", message = messageofrev)
##see all of the reviews i have left##
@app.route("/myReviews",methods=["GET"])
def viewmyReview():
    userid = session.get('user_id')
    messageofrev = review.getmyreviews(userid)
    return render_template("myreviews.html", message = messageofrev)
###edit any of the reviews that apply to me##
@app.route("/editReview/<int:reviewID>",methods=["GET"])
def editReviewget(reviewID):
    messageofrev = review.viewreview(reviewID)
    return render_template("editreview.html", message = messageofrev)
##this saves all of the data from my edit review##

@app.route("/editReview/<int:reviewID>",methods=["POST"])
def editReview(reviewID):
    newcomment = request.form.get("description", 0)
    newrating = request.form.get("rating", 0)
    errorList = validateEDITreview(request.form)
    if len(errorList) > 0:
            messageofrev = review.viewreview(reviewID)
            return render_template('editreview.html', message1 = errorList, message = messageofrev)
    else:
        review.updatereview(reviewID,newcomment,newrating)
        userID = session.get('user_id')
        messageofrev = review.getmyreviews(userID)
        return redirect("/myReviews")
##this simply deletes a review by the review id ands submits it to my reviews##
@app.route("/deleteReview/<int:reviewID>", methods=['POST', 'DELETE', 'GET'])
def deleteReview(reviewID):
    review.deletereview(reviewID)
    userID = session.get("user_id")
    reviews=review.getmyreviews(userID)
    return render_template("myreviews.html",message=reviews)
##starts a new message by loading up the template all users creates the filter##
@app.route("/newMessage",methods=["GET"])
def startnewmessage():
    userlist = user1.getAllusers()
    return render_template("startmessage.html", message = userlist)
##new message posting
@app.route("/newMessage",methods=["POST"])
def postnewmessage():
    senderID = session.get("user_id")
    email = request.form.get("email", 0)
    recieverID = user1.getuserIDfromemail(email)
    content = request.form.get("content", 0)
    listingid = ""
    message.addMessage(senderID, recieverID, listingid, content)
    ##takesyou back to your inbox
    return redirect("/inbox")
##loading up all of your contacts and running sql statements to get numbers of unread messages##
@app.route("/inbox",methods=["GET"])
def inboxload():
    userID = session.get("user_id")
    messageofcontacts = message.getmycontacts(userID)
    messageofunreads = message.getmyunreads(userID)
    return render_template("messageinterface.html", message = messageofcontacts, message2 = messageofunreads)
##pulling up conversation history accorfing to the other persons username##
@app.route("/conversation/<email>",methods=["GET"])
def talktoperson(email):
    userID = session.get("user_id")
    personsinfo = user1.getallfromuserid(email)
    senderID = user1.getuserIDfromemail(email)
    allthemessages = message.gettheconvo(userID,senderID)
    ##updating them as read
    message.updatemessagesasread(userID,senderID)
    return render_template("convo.html", message = allthemessages, message2 = personsinfo)
##when i leave a new message, we store the data into a message, redirect them to the convo page
@app.route("/conversation/<email>",methods=["POST"])
def savethemessage(email):
    senderID = session.get("user_id")
    receiverID = request.form.get("receiverid", 0)
    listingid = ""
    content = request.form.get("content", 0)
    message.addMessage(senderID, receiverID, listingid, content)
    userID = session.get("user_id")
    personsinfo = user1.getallfromuserid(email)
    senderID = user1.getuserIDfromemail(email)
    allthemessages = message.gettheconvo(userID,senderID)
    return render_template("convo.html", message = allthemessages, message2 = personsinfo)
##if i am interested in a listing, this forms the template tosend an inquiry#
@app.route("/newInquiry/<int:listingID>", methods=['POST', 'GET'])
def newInquiry(listingID):
    if request.method == "GET":
        listing_info = listing.getListing(listingID)
        return render_template("newInquiry.html", listing_info=listing_info)
    if request.method == "POST":
        senderID = session.get("user_id")
        receiverID = request.form.get("receiverid", 0)
        content = request.form.get("content", 0)
        listingid = request.form.get("listingid", 0)
        message.addMessage(senderID, receiverID, listingid, content)
        listings=listing.getAllListings()
        categories = Category.getAllCategories()
        return render_template('listings.html',message=listings, categories=categories)
#deleting a profile is as simple as a click
@app.route("/deleteprofile", methods=['POST', 'GET'])
def deleteAccount():
    if request.method == "GET":
        userID = session.get("user_id")
        user1.deleteUser(userID)
        return render_template("profileDeleted.html")


#this ensures the app is running
app.run(debug = True, port=5001)
