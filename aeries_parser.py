def parse_aeries_grades(text):
    """
    Manual grade entry function.
    Returns an empty structure that can be filled in by the user.
    
    Returns:
        dict: Empty structure for manual grade entry
    """
    return {
        'categories': {
            'Assignments': 100.0  # Default category with 100% weight
        },
        'assignments': []  # Will be filled in by the user
    }


def calculate_grade(assignments, categories):
    """
    Calculate final grade based on assignments and category weights.
    This uses ACTUAL POINT VALUES, not percentages.
    
    Args:
        assignments: List of assignment dicts with points_earned, points_possible, category
        categories: Dict of {category_name: weight_percentage}
    
    Returns:
        Dict with overall grade info and category breakdowns
    """
    if not assignments or not categories:
        return {
            'final_grade': 0.0,
            'category_scores': {}
        }
    
    # Group assignments by category
    category_assignments = {cat: [] for cat in categories}
    for assignment in assignments:
        cat = assignment.get('category')
        if cat in category_assignments:
            category_assignments[cat].append(assignment)
    
    # Calculate points for each category
    category_scores = {}
    total_weighted_score = 0
    total_weight = 0
    
    for category, weight in categories.items():
        if not category_assignments[category]:  # No assignments in this category
            continue
            
        # Sum up actual points for this category
        points_earned = 0
        points_possible = 0
        
        for assignment in category_assignments[category]:
            # Always add to points_possible
            points_possible += assignment['points_possible']
            # Only add to points_earned if the assignment is graded
            if assignment['points_earned'] is not None:
                points_earned += assignment['points_earned']
        
        if points_possible > 0:
            category_percentage = (points_earned / points_possible) * 100
            weighted_contribution = (category_percentage * weight) / 100
            
            category_scores[category] = {
                'points_earned': points_earned,
                'points_possible': points_possible,
                'percentage': category_percentage,
                'weight': weight,
                'weighted_contribution': weighted_contribution
            }
            
            total_weighted_score += weighted_contribution
            total_weight += weight
    
    # Calculate final grade
    if total_weight > 0:
        final_grade = total_weighted_score
    else:
        final_grade = 0
    
    return {
        'final_grade': final_grade,
        'category_scores': category_scores
    }
