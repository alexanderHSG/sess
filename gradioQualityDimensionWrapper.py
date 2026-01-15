def calculate_gradients(scores):       
    # Assuming score ranges from -10 to +10 or the highest possible score
    # determine highest absolute possible score
    max_score = 10
    for i in range(len(scores)):
        if abs(scores[i]) > 10:
            max_score = abs(scores[i])

    # Initialize an empty list to hold the gradient strings
    gradients = []

    for score in scores:
        # Map the score to a percentage of the gradient; all scores are treated as positive for gradient calculation
        # This ensures green is always on the left and red on the right
        percentage = (abs(score) / max_score) * 100
        
        # Ensure that for positive scores, the gradient transitions from green to red,
        # and for negative scores, the amount of red increases, but the order stays the same.
        if score >= 0:
            # Transition from more green to red based on the score
            gradient = f"linear-gradient(to right, #00ff00 0%, #00ff00 {percentage+50}%, #ff0000 {percentage+50}%, #ff0000 100%)"
        else:
            # For negative scores, increase the red area while keeping green on the left
            green_percentage = 50 - percentage  # Calculate the remaining percentage for green
            gradient = f"linear-gradient(to right, #00ff00 0%, #00ff00 {green_percentage}%, #ff0000 {green_percentage}%, #ff0000 100%)"
        
        gradients.append(gradient)
    
    return gradients



def html_tranformer(predicted_views, intrinsic_score, contextual_score, representational_score, reputational_score):
    #put arguments in list
    scores = [intrinsic_score, contextual_score, representational_score, reputational_score]
    gradients = calculate_gradients(scores)
            

    predicted_views_html = f"""
    <style>
        /* Base styles for light mode */
        .predicted-views-container {{
            padding: 20px;
            border-radius: 8px;
            background-color: #ffffff; /* Light background color */
            text-align: center;
            margin-top: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            color: #000000; /* Dark text color for contrast */
        }}

        .predicted-views-title {{
            margin: 0;
            font-size: 20px;
            font-weight: bold;
        }}

        .predicted-views-number {{
            margin: 10px 0;
            font-size: 26px;
            font-weight: bold;
        }}

        /* Override styles for dark mode */
        @media (prefers-color-scheme: dark) {{
            .predicted-views-container {{
                background-color: #1F2937; /* Dark background color */
                color: #f0f0f0; /* Light text color for contrast */
            }}
        }}
    </style>
    <div class="predicted-views-container">
        <p class="predicted-views-title">Predicted views 30 days after your upload to a slide-sharing platform (e.g. Speakerdeck.com)</p>
        <p class="predicted-views-number">{predicted_views}</p>
    </div>
    """


    # Generating HTML output with dynamic gradient based on scores
    quality_dimensions_html = f"""
    <style>
        .quality-display {{
            margin-bottom: 20px;
            text-align: center;
        }}

        .quality-display h3 {{
            margin-bottom: 10px;
            color: #ffffff; /* Ensuring visibility on dark backgrounds */
        }}

        .quality-gradient {{
            height: 20px;
            border-radius: 5px;
            width: 100%; /* Ensure the gradient spans the full width of its container */
        }}

        #intrinsic-quality .quality-gradient {{
            background: {gradients[0]};
        }}

        #contextual-quality .quality-gradient {{
            background: {gradients[1]};
        }}

        #representational-quality .quality-gradient {{
            background: {gradients[2]};
        }}

        #reputational-quality .quality-gradient {{
            background: {gradients[3]};
        }}
    </style>

    <div id="ai-feedback">
        <h2 style="color: #ffffff;">AI Feedback Viewer</h2>
        
        <div class="quality-display" id="intrinsic-quality">
            <h3>Intrinsic Quality</h3>
            <div class="quality-gradient"></div>
        </div>
        <div class="quality-display" id="contextual-quality">
            <h3>Contextual Quality</h3>
            <div class="quality-gradient"></div>
        </div>
        <div class="quality-display" id="representational-quality">
            <h3>Representational Quality</h3>
            <div class="quality-gradient"></div>
        </div>
        <div class="quality-display" id="reputational-quality">
            <h3>Reputational Quality</h3>
            <div class="quality-gradient"></div>
        </div>
    </div>
    """

    return quality_dimensions_html, predicted_views_html

