from datetime import datetime
from models import Event, ServicePackage, Booking
from database import db

def is_time_slot_available(date_time):
    # Checks if the requested date and time already exists in the Booking table
    booking = Booking.query.filter_by(date_time=date_time).first()
    return booking is None  # If None, the time slot is available

def create_service_package(name, description, price, event_id):
    # Creates and save a new service package
    service_package = ServicePackage(name=name, description=description, price=price, event_id=event_id)
    db.session.add(service_package)
    db.session.commit()
    return service_package

def update_event(event, makeup_artist_name, location, event_date_time, event_name):
    # Updates the event details
    event.name = event_name
    event.date = event_date_time
    event.location = location
    event.makeup_artist_name = makeup_artist_name
    db.session.commit()

def delete_event(event):
    # Deletes the associated service packages first
    for service_package in event.services:
        db.session.delete(service_package)

    # Then it deletes the event itself
    db.session.delete(event)
    db.session.commit()
