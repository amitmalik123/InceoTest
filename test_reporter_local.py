#!/usr/bin/env python3
"""
Test script to verify test_behaviors measurement data generation
"""

import json
import os
import sys
import glob
from datetime import datetime

# Add the reporter to path
sys.path.insert(0, r'C:\Users\darshan.balakrishna\qeautomation')

from applicationqe.ewmnavbar.framework.reporter.influx_reporter import AllureToInfluxDB


class TestReporter(AllureToInfluxDB):
    """Override push method to just print points"""
    
    def push_to_influxdb(self, points):
        """Override: Don't push, just display the generated points"""
        behavior_count = sum(1 for p in points if 'test_behaviors,' in p)
        execution_count = sum(1 for p in points if 'test_execution2,' in p)
        quality_count = sum(1 for p in points if 'test_quality2,' in p)
        artifacts_count = sum(1 for p in points if 'test_artifacts2,' in p)
        
        print(f"\n[MEASUREMENTS - NO PUSH, JUST DISPLAY]")
        print(f"  test_execution2: {execution_count} point(s)")
        print(f"  test_quality2: {quality_count} point(s)")
        print(f"  test_behaviors: {behavior_count} point(s)")
        print(f"  test_artifacts2: {artifacts_count} point(s)")
        print(f"  Total: {len(points)} point(s)")
        
        print(f"\n{'='*80}")
        print("ALL GENERATED LINE PROTOCOL POINTS:")
        print(f"{'='*80}\n")
        
        for i, point in enumerate(points, 1):
            print(f"[{i}] {point}\n")
        
        return True


if __name__ == '__main__':
    reporter = TestReporter()
    reporter.run()
