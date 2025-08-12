#!/usr/bin/env python3
"""
Test script for CubeSat Distributed Computing System
Tests individual components without requiring full network setup
"""

import time
import json
import subprocess
import sys

def test_prime_check():
    """Test prime number checking function"""
    print("Testing prime number checking...")
    
    # Import the function from slave.py
    try:
        from slave import DistributedComputingSlave
        slave = DistributedComputingSlave()
        
        # Test cases
        test_cases = [
            (2, True),
            (3, True),
            (4, False),
            (17, True),
            (25, False),
            (97, True)
        ]
        
        all_passed = True
        for number, expected in test_cases:
            result = slave.check_prime(number)
            status = "✓" if result == expected else "✗"
            print(f"  {status} {number}: expected {expected}, got {result}")
            if result != expected:
                all_passed = False
                
        if all_passed:
            print("  ✓ All prime check tests passed!")
        else:
            print("  ✗ Some prime check tests failed!")
            
        return all_passed
        
    except Exception as e:
        print(f"  ✗ Error testing prime check: {e}")
        return False


def test_fibonacci():
    """Test Fibonacci calculation function"""
    print("Testing Fibonacci calculation...")
    
    try:
        from slave import DistributedComputingSlave
        slave = DistributedComputingSlave()
        
        # Test cases
        test_cases = [
            (0, 0),
            (1, 1),
            (2, 1),
            (3, 2),
            (4, 3),
            (5, 5),
            (10, 55)
        ]
        
        all_passed = True
        for n, expected in test_cases:
            result = slave.calculate_fibonacci(n)
            status = "✓" if result == expected else "✗"
            print(f"  {status} F({n}): expected {expected}, got {result}")
            if result != expected:
                all_passed = False
                
        if all_passed:
            print("  ✓ All Fibonacci tests passed!")
        else:
            print("  ✗ Some Fibonacci tests failed!")
            
        return all_passed
        
    except Exception as e:
        print(f"  ✗ Error testing Fibonacci: {e}")
        return False


def test_matrix_multiply():
    """Test matrix multiplication function"""
    print("Testing matrix multiplication...")
    
    try:
        from slave import DistributedComputingSlave
        slave = DistributedComputingSlave()
        
        # Test small matrix
        start_time = time.time()
        result = slave.matrix_multiply(10)
        end_time = time.time()
        
        if result.get('completed') and result.get('size') == 10:
            print(f"  ✓ Matrix multiplication (10x10) completed in {end_time - start_time:.3f}s")
            return True
        else:
            print(f"  ✗ Matrix multiplication failed: {result}")
            return False
            
    except Exception as e:
        print(f"  ✗ Error testing matrix multiplication: {e}")
        return False


def test_network_tools():
    """Test if required network tools are available"""
    print("Testing network tools availability...")
    
    tools = [
        ("nmcli", "NetworkManager CLI"),
        ("hostapd", "Host Access Point Daemon"),
        ("iw", "Wireless tools"),
        ("ip", "IP command")
    ]
    
    all_available = True
    for tool, description in tools:
        try:
            result = subprocess.run([tool, "--version"], 
                                  capture_output=True, text=True, check=False)
            if result.returncode == 0 or result.returncode == 1:  # Most tools return 1 for --version
                print(f"  ✓ {tool} ({description}) - available")
            else:
                print(f"  ✗ {tool} ({description}) - not available")
                all_available = False
        except FileNotFoundError:
            print(f"  ✗ {tool} ({description}) - not found")
            all_available = False
            
    return all_available


def test_python_dependencies():
    """Test if required Python packages are available"""
    print("Testing Python dependencies...")
    
    packages = [
        ("scapy", "Network packet manipulation"),
        ("netifaces", "Network interface information"),
        ("psutil", "System and process utilities")
    ]
    
    all_available = True
    for package, description in packages:
        try:
            __import__(package)
            print(f"  ✓ {package} ({description}) - available")
        except ImportError:
            print(f"  ✗ {package} ({description}) - not available")
            all_available = False
            
    return all_available


def test_configuration():
    """Test configuration consistency between master and slave"""
    print("Testing configuration consistency...")
    
    try:
        # Import both modules to check configuration
        import master_hub
        import slave
        
        # Check if SSID and password match
        if (master_hub.HOTSPOT_SSID == slave.MASTER_SSID and 
            master_hub.HOTSPOT_PASSWORD == slave.MASTER_PASSWORD):
            print(f"  ✓ SSID and password match: {master_hub.HOTSPOT_SSID}")
        else:
            print("  ✗ SSID and password mismatch!")
            print(f"    Master: {master_hub.HOTSPOT_SSID}")
            print(f"    Slave: {slave.MASTER_SSID}")
            return False
            
        # Check if IP addresses are consistent
        master_subnet = master_hub.SUBNET.split('/')[0]
        if master_subnet == slave.MASTER_IP:
            print(f"  ✓ IP addresses consistent: {slave.MASTER_IP}")
        else:
            print("  ✗ IP address mismatch!")
            print(f"    Master subnet: {master_subnet}")
            print(f"    Slave master IP: {slave.MASTER_IP}")
            return False
            
        return True
        
    except Exception as e:
        print(f"  ✗ Error testing configuration: {e}")
        return False


def main():
    """Run all tests"""
    print("=== CubeSat Distributed Computing System Test ===")
    print("")
    
    tests = [
        ("Python Dependencies", test_python_dependencies),
        ("Network Tools", test_network_tools),
        ("Configuration", test_configuration),
        ("Prime Check", test_prime_check),
        ("Fibonacci", test_fibonacci),
        ("Matrix Multiply", test_matrix_multiply)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            results.append((test_name, False))
        print("")
        
    # Summary
    print("=== Test Summary ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! System is ready for deployment.")
        return 0
    else:
        print("Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
