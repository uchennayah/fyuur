#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
from urllib import response
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)
from models import *
# TODO: connect to a local postgresql database - Done in config.py

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  places = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()  
  for city_state in places:
    city = city_state[0]
    state = city_state[1]
    venues = Venue.query.filter_by(city=city, state=state).all()   
    data.append({
      "city": city,
      "state": state,
      "venues": venues
      })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  to_search = request.form['search_term']
  data_venue=[]
  try:
    find_vens= Venue.query.filter(Venue.name.ilike('%' + to_search + '%')).all()
    result['error'] = error
    for ven in find_vens:
      data_venue.append({
        'id':Venue.id,
        'name':Venue.name,
        'upcomming_shows': Show.query.filter(Show.venue_id == ven.id, Show.date_time>datetime.utcnow()).count()
      })
  except:
    error = True 
  finally:
     result={
     'count': len(find_vens),
     'data':data_venue
   }

  return render_template('pages/search_venues.html', results=result, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter_by(id = venue_id).all()[0]
  venue_data = None
  error = False
  try:
    shows = Show.query.filter_by(venue_id=venue_id).join(Artist, Show.show_artist_id == Artist.id).all()
    coming_Shows = []
    past_Shows = []
    for show in shows:
      showx = {
          'artist_id': show.show_artist_id,
          'start_time': str(show.date_time),
          'artistName': show.artist.name,
          'artistImageLink': show.artist.image_link,
          'genre': show.venue.genres
      }
      if show.startTime > datetime.utcnow():
        coming_Shows.append(showx)
      else:
        past_Shows.append(showx)
    venue_data = {'id': venue.id, 
              'name': venue.name,
              'city': venue.city, 
              "state": venue.state, 
              'adress': venue.address, 
              "facebook_link": venue.facebook_link, 
              'genres': venue.genres,
              "phone": venue.phone,
              "image_link": venue.image_link,
              "seeking_talent": venue.seeking_talent, 
              "seeking_description": venue.seeking_desc, 
              "past_shows": past_Shows,
          "coming_shows": coming_Shows}
  except :
      error = True
  if not error:
    return render_template('pages/show_venue.html', venu =venue_data)
  else:
    return render_template('errors/404.html')
 

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    venue = Venue(
      name=request.form['name'],
      genres=request.form.getlist('genres'),
      address=request.form['address'],
      city=request.form['city'],
      state=request.form['state'],
      phone=request.form['phone'],
      website_link=request.form['website_link'],
      facebook_link=request.form['facebook_link'],
      image_link=request.form['image_link'],
      seeking_talent= True if 'seeking_talent' in request.form else False,
      seeking_description=request.form['seeking_description'],
    )
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()
  if error: 
    flash('An error occurred. Venue ' + request.form['name']+ ' could not be listed.')
  if not error: 
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id): 
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter(Venue.id == venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  real_data= []
  error = False
  try:
    artistes = Artist.query.all()
    for arti_stes in artistes:
      real_data.append({'id':Artist.id,'name':Artist.name})
  except:
    error = True 
  finally:
    if not error:
      return render_template('pages/artists.html', artists=real_data)
    else:
      render_template('errors/500.html')

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  to_search = request.form['search_term']
  a_respond = Artist.query.filter(Artist.name.ilike('%' + to_search + '%')).all()
  show_results = []
  for respond in a_respond:
    show_results.append({
      'id':respond.id,
      'name':respond.name,
      'num_upcoming_shows': Show.query.filter(Show.show_artist_id == respond.id, Show.date_time > datetime.now()).count()
    })
    result = {
    'count': len(a_respond),
    'data':show_results
    }
    return render_template('pages/search_artists.html', results=result, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
 
  find_artist= Artist.query.filter_by(id = artist_id).all()[0]
  shows = Show.query.filter_by(artist_id=find_artist.id).join(Venue,Show.show_venue_id==Venue.id).all()
  error =  False
  try:
    upcoming_artist= []
    previous_artist= []
    for show in shows:
      # artist show object
      artist_show = {
        'venue_id':show.venue_id,
        'venue_image_link': show.venue.image_link,
        'start_time': str(show.startTime),
        'venue_name':show.venue.name
      }
      if show.date_time>datetime.utcnow():
        upcoming_artist.append(artist_show)
      else:
        previous_artist.append(artist_show)
    
    just_return = {
      "id": find_artist.id,
      "genres": find_artist.genres,
      "name": find_artist.name,
      "city": find_artist.city,
      "phone": find_artist.phone,
      "state": find_artist.state,
      "seek_description": find_artist.seeking_description,
      "seek_venue": find_artist.seeking_venue,
      "facebook_link": find_artist.facebook_link,
      "image_link": find_artist.image_link,
      "upcoming_shows": upcoming_artist,
      "past_shows":previous_artist,
      
    }
  except:
    error = True
    
  finally:
    if not error:
      return render_template('pages/show_artist.html', art =just_return)
    else:
      return render_template('errors/404.html')
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  form_art = Artist.query.filter_by(id = artist_id).all()[0]
  artist={
      "id": form_art.id,
      "name": form_art.name,
      "city": form_art.city,
      "genres": form_art.genres,
      "phone": form_art.phone,
      "state": form_art.state,
      "seek_description": form_art.seeking_description,
      "seek_venue": form_art.seeking_venue,
      "facebook_link": form_art.facebook_link,
      "image_link": form_art.image_link,
      
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False
  try:

    venue = VenueForm()
    venue = Venue(
        name=request.form.name.data,
        address=request.form.address.data, 
        city=request.form.city.data,
        state=request.form.state.data, 
        phone=request.form.phone.data,
        genres=request.form.genres.data,
        facebook_link=request.form.facebook_link.data,
        image_link=request.form.image_link.data
    )
    db.session.add(ven)
    db.session.commit()
  except:
    db.session.rollback()
   
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    flash('An error occurred. Venue ' +
        request.form['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).all()[0]
  venue={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "seeking_description": venue.seek_description,
    "seeking_talent": venue.seek_talent,
    "image_link": venue.image_link,
    "facebook_link": venue.facebook_link,
  }
  
  

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  error = False
  try:
    form = VenueForm(request.form)
    venue = Venue(
        name=form.name.data, 
        city=form.city.data,
        address=form.address.data,
        state=form.state.data, 
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data
    )
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    
  finally:
    db.session.close()
  if error:
  # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue_id', show_venue_id=show_venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  form=ArtistForm()
  error= False
  # TODO: modify data to be the data object returned from db insertion
  try:
    artist = Artist(
      name = form.name.data, city = form.city.data,
      facebook_link = form.facebook_link.data,
      genres = form.genres.data,
      image_link = form.image_link.data,
      state = form.state.data, phone = form.phone.data
      )
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    
  finally:
    db.session.close()
  # on successful db insert, flash success
  if not error and  form.validate_on_submit(): 
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  else:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
   error = False
   real_venue = Show.query.join(Venue,Show.show_venue_id == Venue.id).join(Artist,Show.show_artist_id == Artist.id).all()
   responding = list()
   for place in real_venue:
  # num_shows should be aggregated based on number of upcoming shows per venue.
    responding.append({
    'venue_name': Show.venue.name,
    'venue_id': Show.venue_id,
    'artist_name':Show.artist.name,
    'artist_image_link': Show.artist.image_link,
    'artist_id': Show.artist_id,
    'start_time': str(Show.startTime)
    })
    size = len(responding)
    return render_template('pages/shows.html', shows=responding)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=forms)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  success = True
  try:
    form = ShowForm(request.form)
    if form.validate_on_submit():
      add = Show (
      date_time = form.date_time.data,
      show_venue_id = form.venue_id.data,
      show_artist_id = form.artist_id.dat )

    db.session.add(to_add)
    db.session.commit()
  except:
    error =True
    db.session.rollback()
    
  #finally:
    db.session.close()
  # on successful db insert, flash success
  if success:  
    flash('Success')
 
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  else:  
    flash('An error occurred. Show not listed.')
    return render_template('pages/home.html')
 

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
