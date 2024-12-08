import logging
import sqlite3

from common.presenter import Presenter
from messages.messages import (PROFILE_CREATE_SUCCESS, PROFILE_UPDATE_SUCCESS, DB_ERROR, CREATE_OR_UPDATE_PROFILE_ERROR,
                               CREATE_PROFILE_ERROR)
from models.profile import ProfileModel


class ProfilePresenter(Presenter):
    def __init__(self, view):
        super().__init__(view, ProfileModel())

    def get_profile_details(self, username):
        """
        Fetches profile details by username using the model.
        Returns a dictionary with profile information, None if not found, or an error message.
        """
        try:
            profile = self.model.get_profile_by_username(username)

            # If no profile is found, return None
            if profile is None:
                return None

            # Ensure the profile object has the necessary attributes before returning
            return {
                "ID": profile.id,
                "User ID": profile.user_id,
                "Full Name": getattr(profile, 'fullname', ''),
                "Position": getattr(profile, 'position', ''),
                "Phone Number": getattr(profile, 'phone_number', ''),
            }
        except Exception as e:
            # Return an error dictionary for the caller to handle
            return {"error": f"Could not retrieve profile for {username}: {str(e)}"}

    def load_profile(self, username):
        # Use the presenter to get profile data
        profile_data = self.get_profile_details(username)

        if profile_data is None:
            # If no profile data is found
            self.view.name_input.setText("")
            self.view.operative_unit_input.setText("")
            self.view.telephone_input.setText("")

        elif "error" in profile_data:
            return
        else:
            full_name = profile_data.get("Full Name", "")
            position = profile_data.get("Position", "")
            phone_number = str(profile_data.get("Phone Number", ""))

            # Populate the form fields
            self.view.name_input.setText(full_name)
            self.view.operative_unit_input.setText(position)
            self.view.telephone_input.setText(phone_number)

    def create_or_update_profile(self, username, fullname, position, phone_number):
        """
        Create a profile if the user does not exist; otherwise, update the existing profile.
        """
        try:
            # Attempt to fetch the profile
            profile_data = self.get_profile_details(username)

            # If profile exists, update it
            if profile_data:
                self.model.update(username, "fullname", fullname)
                self.model.update(username, "position", position)
                self.model.update(username, "phone_number", phone_number)
                self.view.display_success(f"{PROFILE_UPDATE_SUCCESS}")
            else:
                # Profile not found; create a new one
                self.model.create(username, fullname, position, phone_number)
                self.view.display_success(f"{PROFILE_CREATE_SUCCESS}")

        except sqlite3.Error as db_error:
            # Handle database-specific errors
            self.view.display_error(f"{db_error}")
        except Exception as e:
            # Handle unexpected errors
            self.view.display_error(f"{CREATE_OR_UPDATE_PROFILE_ERROR}")
            logging.error(f"An unexpected error occurred: {str(e)}")

