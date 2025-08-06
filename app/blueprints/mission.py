from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from contactform.mission import get_all_missions, create_mission, get_mission

mission_bp = Blueprint('mission', __name__, url_prefix='/mission')

@mission_bp.route("/")
def mission_list():
    """First page: Show list of missions"""
    try:
        # Get missions from database
        missions = get_all_missions()
        
        # Convert to dictionary format for template compatibility
        mission_data = []
        for mission in missions:
            mission_name = mission.pre_defined_fields.get("name", f"Mission {mission.id}")
            mission_data.append({
                "id": mission.id,
                "name": mission_name,
                "created_date": mission.created_date.strftime("%Y-%m-%d"),
                "status": "Active",  # Default status for now
            })
    except Exception as e:
        flash(f"Error loading missions: {str(e)}", "error")
        # Fallback to sample data if database fails
        mission_data = [
            {
                "id": 1,
                "name": "Marketing Campaign 2025",
                "created_date": "2025-08-01",
                "status": "Active",
            },
            {
                "id": 2,
                "name": "Customer Survey",
                "created_date": "2025-07-15",
                "status": "Draft",
            },
            {
                "id": 3,
                "name": "Product Feedback",
                "created_date": "2025-07-20",
                "status": "Active",
            },
        ]
    
    return render_template("mission_list.html", missions=mission_data)

@mission_bp.route("/create", methods=["GET", "POST"])
def create_mission_route():
    """Create new mission"""
    if request.method == "POST":
        mission_name = request.form.get("mission_name")
        if not mission_name:
            flash("Mission name is required!", "error")
            return render_template("create_mission.html")
        
        try:
            # Create mission with basic fields
            pre_defined_fields = {
                "name": mission_name,
                "email": "",
                "message": "",
                "phone": "",
                "company": ""
            }
            
            mission = create_mission(mission_name, pre_defined_fields)
            flash(f'Mission "{mission_name}" created successfully!', "success")
            return redirect(url_for("mission.mission_list"))
        except Exception as e:
            flash(f"Error creating mission: {str(e)}", "error")
            return render_template("create_mission.html")
    
    return render_template("create_mission.html")

@mission_bp.route("/<int:mission_id>/select")
def select_mission(mission_id: int):
    """Select a mission and store in session"""
    try:
        mission = get_mission(mission_id)
        if mission:
            session["current_mission_id"] = mission_id
            mission_name = mission.pre_defined_fields.get("name", f"Mission {mission.id}")
            session["current_mission_name"] = mission_name
            flash(f'Mission "{mission_name}" selected!', "info")
        else:
            flash("Mission not found!", "error")
            return redirect(url_for("mission.mission_list"))
    except Exception as e:
        flash(f"Error selecting mission: {str(e)}", "error")
        return redirect(url_for("mission.mission_list"))
    
    return redirect(url_for("config.config_page"))
