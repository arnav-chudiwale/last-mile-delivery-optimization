#Problem = 
Reality - orders arrive continuosly throughout the day

#Approach = Time-based re-planning

1) 8am - 1000 packages arrive = Plan initial route with existing vehicles
2) 10am - 1000+ packages arrive = reoptimize remaining capacity + new orders
3) 12pm - 906+ packages arrive = Final adjustment
4) 2pm - 1000+ packages arrive = Emergency Outsourcing decision 

#Decisions to make -
1) When to dispatch vehicles = wait vs start early
2) When to reoptimize?
3) When to outsource to 3PL

#Metrics
1) Route Efficiency - Distance travelled per package
2) On-time delivery - % orders delivered within time
3) Utilization - % of in-house vehicle capacity used 
4) Replanning cost - co-ordination overhead 


