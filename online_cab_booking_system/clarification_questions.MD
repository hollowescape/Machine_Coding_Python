Understanding the Problem & Clarifying Questions
First, I'll clarify some details and state my assumptions for this implementation.

Clarifying Questions (and my assumed answers for this design):

Driver Availability: How do drivers become "available"? Do they explicitly toggle their status, or does it automatically become AVAILABLE after a ride COMPLETED?

Assumption: Drivers' status automatically becomes AVAILABLE upon COMPLETED ride. They can also be AVAILABLE by default when registered.

Closest Driver Tie-breaker: If multiple drivers are equidistant, how do we choose?

Assumption: Any one of them can be chosen. For determinism in testing, we'll pick the one with the lowest driver_id (lexicographically).

Ride Cancellation: Is ride cancellation a required feature?

Assumption: While not explicitly requested, ride cancellation is a critical feature for real-world systems. It should allow riders or drivers to cancel a ride before it starts.

Driver Acceptance/Rejection: Do drivers get to accept/reject