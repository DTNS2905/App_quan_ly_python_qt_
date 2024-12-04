import sqlite3

from PyQt6.QtWidgets import QMessageBox

from common.presenter import Presenter
from messages.messages import (PROFILE_CREATE_SUCCESS, PROFILE_UPDATE_SUCCESS, DB_ERROR, CREATE_OR_UPDATE_PROFILE_ERROR,
                               CREATE_PROFILE_ERROR)
from models.profile import ProfileModel
from ui_components.custom_messgae_box import CustomMessageBox


class ProfilePresenter(Presenter):
    def __init__(self, view):
        super().__init__(view, ProfileModel())

    def get_profile_details(self, username):
        try:
            profile = self.model.get_profile_by_username(username)
            return {
                "ID": profile.id,
                "User ID": profile.user_id,
                "Full Name": profile.fullname,
                "Position": profile.position,
                "Phone Number": profile.phone_number,
                "Created At": profile.created_at,
                "Updated At": profile.updated_at,
            }
        except Exception as e:
            self.view.display_error(CREATE_PROFILE_ERROR)
            print({"success": False, "error": str(e)})

    def load_profile(self, username):
        # Use the presenter to get profile data
        profile_data = self.get_profile_details(username)

        if "error" in profile_data:
            self.display_error("Error", profile_data["error"])
            return

        # Populate QLineEdit widgets with profile data
        self.view.name_input.setText(profile_data["Full Name"])
        self.view.operative_unit_input.setText(profile_data["Position"])
        self.view.telephone_input.setText(str(profile_data["Phone Number"]))

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
            print(f"An unexpected error occurred: {str(e)}")


