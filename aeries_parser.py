import re

def parse_aeries_grades(text):
    """
    Parse copy-pasted Aeries grade text and extract:
    - Class name and teacher
    - Category weights
    - Individual assignments
    
    Returns a dictionary with parsed data
    """
    result = {
        'class_name': '',
        'teacher_name': '',
        'categories': {},  # {category_name: weight}
        'assignments': []
    }
    
    # Extract class name (look for pattern like "IB Lang/LitHL1A- Trimester 1")
    class_match = re.search(r'<<\s*\d+-\s*([^>]+?)-\s*Trimester[^>]*>>', text)
    if class_match:
        # Extract just the class name part, removing leading number and dash
        class_name_full = class_match.group(1).strip()
        result['class_name'] = class_name_full
    
    # Extract teacher name and email (more flexible pattern)
    teacher_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})', text)
    if teacher_match:
        result['teacher_name'] = teacher_match.group(1).strip()
    
    # Parse category totals from the Totals section
    # The format in table view has each field on separate lines
    lines = text.split('\n')
    in_totals_section = False
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Look for "Totals" or "Category" header
        if 'Totals' in line or line_stripped == 'Category':
            in_totals_section = True
            continue
        
        # Parse category data when in totals section
        if in_totals_section:
            # Look for category names followed by percentage weight
            if line_stripped in ['Classwork', 'Labs', 'Tests & Quizzes', 'Homework', 'Projects']:
                category_name = line_stripped
                # Look ahead for the percentage of grade (next line or nearby)
                for j in range(i+1, min(i+5, len(lines))):
                    weight_match = re.match(r'^([\d.]+)%$', lines[j].strip())
                    if weight_match:
                        weight = float(weight_match.group(1))
                        result['categories'][category_name] = weight
                        break
            
            # Stop if we hit "Transfer Grade" or other end markers
            if 'Transfer Grade' in line or 'Enable Color' in line:
                break
    
    # Parse individual assignments from table view
    # Strategy: Find assignment numbers, then look for the pattern in subsequent lines
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for assignment number at the start of a line (just digits)
        # Skip table headers and other numeric-only lines that aren't assignment numbers
        if re.match(r'^(\d+)$', line) and line not in ['1', '2', '3', '4', '5'] or \
           (re.match(r'^\d+$', line) and i > 0 and 'DescriptionCategory' not in text[:text.find(line)+100]):
            
            # Check if this could be an assignment number by looking ahead
            assignment_num = line
            temp_i = i + 1
            
            # Try to find description (should be text, not empty, not a known header)
            if temp_i >= len(lines):
                i += 1
                continue
                
            potential_description = lines[temp_i].strip()
            
            # Skip if it's a header, empty, or looks like data
            if not potential_description or \
               potential_description in ['Description', 'Category', 'Score', '#DescriptionCategoryScore', '/', 'Yes', 'No'] or \
               re.match(r'^[\d.]+$', potential_description) or \
               re.match(r'^\d{2}/\d{2}/\d{4}$', potential_description):
                i += 1
                continue
            
            description = potential_description
            temp_i += 1
            
            # Next should be category
            if temp_i >= len(lines):
                i += 1
                continue
                
            potential_category = lines[temp_i].strip()
            if potential_category not in ['Classwork', 'Labs', 'Tests & Quizzes', 'Homework', 'Projects']:
                i += 1
                continue
            
            category = potential_category
            temp_i += 1
            
            # Now collect the next several lines to find score pattern
            # Format is: points_earned on one line, "/" on another, points_possible on another
            score_data = []
            for j in range(20):  # Look ahead up to 20 lines
                if temp_i >= len(lines):
                    break
                next_line = lines[temp_i].strip()
                
                # Stop if we hit another assignment number
                if re.match(r'^\d+$', next_line) and j > 5:  # Allow first few lines to have numbers
                    break
                    
                # Stop if we hit totals section
                if next_line in ['Totals', 'Category', 'Total']:
                    break
                
                score_data.append(next_line)
                temp_i += 1
            
            # Join the collected lines and try to find the score pattern
            score_text = ' '.join(score_data)
            
            # Check if grading is complete (only include assignments where grading is complete)
            # Look for "No" at the end which indicates grading is NOT complete
            grading_complete = True
            # Check if the last few items contain "No" which means not graded yet
            if len(score_data) > 0:
                last_items = score_data[-3:]  # Check last 3 items
                # If we see "No" without "Yes" nearby, grading is not complete
                if 'No' in last_items and 'Yes' not in last_items:
                    grading_complete = False
            
            # Only include assignments where grading is complete
            if not grading_complete:
                i = temp_i
                continue
            
            # Look for the score pattern: "number / number" or "/ number" (empty score)
            # The first occurrence is the actual score (second is # Correct which we ignore)
            score_match = re.search(r'([\d.]*)\s*/\s*([\d.]+)', score_text)
            if score_match:
                points_earned_str = score_match.group(1).strip()
                points_earned = float(points_earned_str) if points_earned_str else None
                points_possible = float(score_match.group(2))
                
                # Extract comment if present
                comment_patterns = [
                    r'retake\s*\d*', r'Resubmit\s*\d*', r'Late',
                    r'Ground\s*-?\d*', r'sandpaper', r'Test Corrections'
                ]
                comment = ''
                for pattern in comment_patterns:
                    comment_match = re.search(pattern, score_text, re.IGNORECASE)
                    if comment_match:
                        comment = comment_match.group(0).strip()
                        break
                
                assignment = {
                    'description': description,
                    'category': category,
                    'points_earned': points_earned,
                    'points_possible': points_possible,
                    'comment': comment
                }
                result['assignments'].append(assignment)
                
                # Move index forward
                i = temp_i
                continue
        
        i += 1
    
    return result


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
    # Group assignments by category
    category_assignments = {}
    for assignment in assignments:
        cat = assignment['category']
        if cat not in category_assignments:
            category_assignments[cat] = []
        category_assignments[cat].append(assignment)
    
    # Calculate points for each category
    category_scores = {}
    total_weighted_score = 0
    total_weight = 0
    
    for category, weight in categories.items():
        if category not in category_assignments:
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
