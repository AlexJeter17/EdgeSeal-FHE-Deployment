"""
IOT_Data_Encryption.py - Simplified FHE Encryption for IoT Sensor Data
------------------------------------------------------------------------
Focused encryption class for IoT sensor data (bio-signals and motion/location)
using TenSEAL CKKS scheme.

Supports:
- Bio-signal data: SpO2, ECG, Heart Rate
- Motion/Location data: Accelerometer, Gyroscope, GPS coordinates
- Simple API for encryption and decryption
- Returns encrypted data ready for testing and processing
"""

import tenseal as ts
import numpy as np
from typing import Union, List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class IOTEncryptionConfig:
    """Simplified configuration for IoT data encryption"""
    poly_modulus_degree: int = 8192
    global_scale: int = 2**40

    def get_coeff_mod_bit_sizes(self) -> List[int]:
        """Get coefficient modulus bit sizes based on poly_modulus_degree"""
        if self.poly_modulus_degree == 8192:
            return [60, 40, 40, 60]
        elif self.poly_modulus_degree == 16384:
            return [60, 40, 40, 40, 40, 60]
        else:
            return [60, 40, 40, 60]


class IOTDataEncryptor:
    """
    Simplified encryption class for IoT sensor data

    Features:
    - Easy encryption of bio-signals (SpO2, ECG, Heart Rate)
    - Motion and location data support (Accelerometer, Gyroscope, GPS)
    - Returns encrypted data ready for testing
    - Minimal configuration required
    """

    def __init__(self, config: IOTEncryptionConfig = None):
        """
        Initialize IoT Data Encryptor

        Args:
            config: IOTEncryptionConfig object (uses default if None)
        """
        self.config = config or IOTEncryptionConfig()
        self.context = self._create_context()

    def _create_context(self) -> ts.Context:
        """Create TenSEAL CKKS encryption context"""
        context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=self.config.poly_modulus_degree,
            coeff_mod_bit_sizes=self.config.get_coeff_mod_bit_sizes()
        )
        context.generate_galois_keys()
        context.global_scale = self.config.global_scale
        return context

    # ==================== CORE ENCRYPTION METHODS ====================

    def encrypt_data(self, data: Union[float, List[float], np.ndarray]) -> ts.CKKSVector:
        """
        Main encryption method - encrypts any numerical data

        Args:
            data: Single value, list, or numpy array

        Returns:
            Encrypted CKKSVector ready for testing
        """
        # Convert to list format
        if isinstance(data, (int, float)):
            data_list = [float(data)]
        elif isinstance(data, np.ndarray):
            data_list = data.flatten().tolist()
        elif isinstance(data, list):
            data_list = data
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")

        # Encrypt and return
        return ts.ckks_vector(self.context, data_list)

    def decrypt_data(self, encrypted_data: ts.CKKSVector) -> List[float]:
        """
        Decrypt encrypted data back to plaintext

        Args:
            encrypted_data: Encrypted CKKSVector

        Returns:
            List of decrypted values
        """
        return encrypted_data.decrypt()

    # ==================== BIO-SIGNAL ENCRYPTION ====================

    def encrypt_spo2(self, spo2_values: Union[List[float], np.ndarray]) -> ts.CKKSVector:
        """
        Encrypt SpO2 (blood oxygen saturation) sensor data

        Args:
            spo2_values: SpO2 readings (typically 90-100%)

        Returns:
            Encrypted SpO2 data
        """
        if isinstance(spo2_values, np.ndarray):
            spo2_values = spo2_values.tolist()

        return ts.ckks_vector(self.context, spo2_values)

    def encrypt_ecg(self, ecg_signal: Union[List[float], np.ndarray]) -> ts.CKKSVector:
        """
        Encrypt ECG (electrocardiogram) sensor data

        Args:
            ecg_signal: ECG voltage readings (in mV)

        Returns:
            Encrypted ECG data
        """
        if isinstance(ecg_signal, np.ndarray):
            ecg_signal = ecg_signal.tolist()

        return ts.ckks_vector(self.context, ecg_signal)

    def encrypt_heart_rate(self, hr_values: Union[List[float], np.ndarray]) -> ts.CKKSVector:
        """
        Encrypt heart rate sensor data

        Args:
            hr_values: Heart rate readings (BPM)

        Returns:
            Encrypted heart rate data
        """
        if isinstance(hr_values, np.ndarray):
            hr_values = hr_values.tolist()

        return ts.ckks_vector(self.context, hr_values)

    def encrypt_biosignal_batch(self, spo2: np.ndarray = None,
                                ecg: np.ndarray = None,
                                heart_rate: np.ndarray = None) -> Dict[str, ts.CKKSVector]:
        """
        Encrypt multiple bio-signals at once

        Args:
            spo2: SpO2 data (optional)
            ecg: ECG data (optional)
            heart_rate: Heart rate data (optional)

        Returns:
            Dictionary with encrypted bio-signals
        """
        encrypted_data = {}

        if spo2 is not None:
            encrypted_data['spo2'] = self.encrypt_spo2(spo2)

        if ecg is not None:
            encrypted_data['ecg'] = self.encrypt_ecg(ecg)

        if heart_rate is not None:
            encrypted_data['heart_rate'] = self.encrypt_heart_rate(heart_rate)

        return encrypted_data

    # ==================== MOTION & LOCATION ENCRYPTION ====================

    def encrypt_accelerometer(self, x: np.ndarray, y: np.ndarray, z: np.ndarray) -> Dict[str, ts.CKKSVector]:
        """
        Encrypt 3-axis accelerometer data

        Args:
            x: X-axis acceleration values
            y: Y-axis acceleration values
            z: Z-axis acceleration values

        Returns:
            Dictionary with encrypted x, y, z axes
        """
        return {
            'x': self.encrypt_data(x),
            'y': self.encrypt_data(y),
            'z': self.encrypt_data(z)
        }

    def encrypt_gyroscope(self, x: np.ndarray, y: np.ndarray, z: np.ndarray) -> Dict[str, ts.CKKSVector]:
        """
        Encrypt 3-axis gyroscope data

        Args:
            x: X-axis rotation values
            y: Y-axis rotation values
            z: Z-axis rotation values

        Returns:
            Dictionary with encrypted x, y, z axes
        """
        return {
            'x': self.encrypt_data(x),
            'y': self.encrypt_data(y),
            'z': self.encrypt_data(z)
        }

    def encrypt_gps_coordinates(self, latitudes: Union[List[float], np.ndarray],
                                longitudes: Union[List[float], np.ndarray]) -> Dict[str, ts.CKKSVector]:
        """
        Encrypt GPS coordinate data

        Args:
            latitudes: Latitude values
            longitudes: Longitude values

        Returns:
            Dictionary with encrypted latitude and longitude
        """
        return {
            'latitude': self.encrypt_data(latitudes),
            'longitude': self.encrypt_data(longitudes)
        }

    def encrypt_motion_batch(self, accel_data: Tuple[np.ndarray, np.ndarray, np.ndarray] = None,
                            gyro_data: Tuple[np.ndarray, np.ndarray, np.ndarray] = None) -> Dict[str, Dict[str, ts.CKKSVector]]:
        """
        Encrypt multiple motion sensors at once

        Args:
            accel_data: Tuple of (x, y, z) accelerometer data
            gyro_data: Tuple of (x, y, z) gyroscope data

        Returns:
            Dictionary with encrypted motion data
        """
        encrypted_data = {}

        if accel_data is not None:
            encrypted_data['accelerometer'] = self.encrypt_accelerometer(*accel_data)

        if gyro_data is not None:
            encrypted_data['gyroscope'] = self.encrypt_gyroscope(*gyro_data)

        return encrypted_data

    # ==================== BASIC OPERATIONS ON ENCRYPTED DATA ====================

    def compute_encrypted_mean(self, encrypted_vector: ts.CKKSVector, length: int) -> float:
        """
        Compute mean of encrypted data (requires decryption)

        Args:
            encrypted_vector: Encrypted data
            length: Original data length

        Returns:
            Mean value (decrypted)
        """
        decrypted = encrypted_vector.decrypt()
        return sum(decrypted[:length]) / length

    def add_encrypted(self, enc1: ts.CKKSVector, enc2: ts.CKKSVector) -> ts.CKKSVector:
        """
        Add two encrypted vectors

        Args:
            enc1: First encrypted vector
            enc2: Second encrypted vector

        Returns:
            Encrypted sum
        """
        return enc1 + enc2

    def multiply_encrypted(self, enc1: ts.CKKSVector, enc2: ts.CKKSVector) -> ts.CKKSVector:
        """
        Multiply two encrypted vectors element-wise

        Args:
            enc1: First encrypted vector
            enc2: Second encrypted vector

        Returns:
            Encrypted product
        """
        return enc1 * enc2

    def scale_encrypted(self, encrypted_vector: ts.CKKSVector, scalar: float) -> ts.CKKSVector:
        """
        Multiply encrypted vector by plaintext scalar

        Args:
            encrypted_vector: Encrypted data
            scalar: Scaling factor

        Returns:
            Scaled encrypted data
        """
        return encrypted_vector * scalar

    # ==================== UTILITY METHODS ====================

    def get_context_info(self) -> Dict:
        """Get encryption context information"""
        return {
            'poly_modulus_degree': self.config.poly_modulus_degree,
            'global_scale': self.config.global_scale,
            'coeff_mod_bit_sizes': self.config.get_coeff_mod_bit_sizes()
        }

    def verify_encryption(self, original_data: Union[List[float], np.ndarray],
                         encrypted_data: ts.CKKSVector,
                         tolerance: float = 1e-3) -> bool:
        """
        Verify encryption by decrypting and comparing

        Args:
            original_data: Original plaintext data
            encrypted_data: Encrypted data
            tolerance: Acceptable error tolerance

        Returns:
            True if encryption is valid within tolerance
        """
        if isinstance(original_data, np.ndarray):
            original_data = original_data.tolist()

        decrypted = encrypted_data.decrypt()

        # Compare values within tolerance
        for orig, dec in zip(original_data, decrypted):
            if abs(orig - dec) > tolerance:
                return False
        return True


# ==================== MOCK DATA GENERATORS FOR TESTING ====================

def generate_mock_spo2(duration_seconds: int = 60) -> np.ndarray:
    """Generate realistic mock SpO2 data for testing"""
    n_samples = duration_seconds
    base_spo2 = 97.5
    t = np.linspace(0, duration_seconds, n_samples)

    variation = 1.5 * np.sin(2 * np.pi * 0.05 * t)
    noise = np.random.normal(0, 0.3, n_samples)

    spo2_data = base_spo2 + variation + noise
    return np.clip(spo2_data, 90, 100)


def generate_mock_heart_rate(duration_seconds: int = 60) -> np.ndarray:
    """Generate realistic mock heart rate data for testing"""
    n_samples = duration_seconds
    base_hr = 72
    t = np.linspace(0, duration_seconds, n_samples)

    slow_variation = 5 * np.sin(2 * np.pi * 0.02 * t)
    fast_variation = 3 * np.sin(2 * np.pi * 0.25 * t)
    noise = np.random.normal(0, 1, n_samples)

    hr_data = base_hr + slow_variation + fast_variation + noise
    return np.clip(hr_data, 50, 100)


def generate_mock_accelerometer(duration_seconds: int = 10, sampling_rate: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate realistic mock 3-axis accelerometer data"""
    n_samples = duration_seconds * sampling_rate
    t = np.linspace(0, duration_seconds, n_samples)

    # Simulate gravity on z-axis and some motion
    x = 0.1 * np.sin(2 * np.pi * 2 * t) + np.random.normal(0, 0.05, n_samples)
    y = 0.1 * np.cos(2 * np.pi * 2 * t) + np.random.normal(0, 0.05, n_samples)
    z = 9.81 + 0.2 * np.sin(2 * np.pi * 1 * t) + np.random.normal(0, 0.1, n_samples)

    return x, y, z


def generate_mock_gps(num_points: int = 100) -> Tuple[np.ndarray, np.ndarray]:
    """Generate realistic mock GPS coordinates (random walk)"""
    # Starting point (example: somewhere in California)
    start_lat, start_lon = 37.7749, -122.4194

    # Random walk
    lat_changes = np.random.normal(0, 0.001, num_points)
    lon_changes = np.random.normal(0, 0.001, num_points)

    latitudes = start_lat + np.cumsum(lat_changes)
    longitudes = start_lon + np.cumsum(lon_changes)

    return latitudes, longitudes


# ==================== DEMO FUNCTION ====================

def demo_iot_encryption():
    """
    Demonstration of IoT data encryption
    """
    print("="*60)
    print("IOT DATA ENCRYPTION DEMO")
    print("="*60)

    # Initialize encryptor
    print("\n1. Initializing IOT Data Encryptor...")
    encryptor = IOTDataEncryptor()
    print(f"   Context Info: {encryptor.get_context_info()}")

    # Test bio-signal encryption
    print("\n2. Encrypting Bio-Signal Data...")

    # Generate and encrypt SpO2
    spo2_data = generate_mock_spo2(60)
    encrypted_spo2 = encryptor.encrypt_spo2(spo2_data)
    print(f"   SpO2: {len(spo2_data)} samples encrypted")
    print(f"   Original mean: {np.mean(spo2_data):.2f}%")
    print(f"   Encrypted mean: {encryptor.compute_encrypted_mean(encrypted_spo2, len(spo2_data)):.2f}%")

    # Generate and encrypt Heart Rate
    hr_data = generate_mock_heart_rate(60)
    encrypted_hr = encryptor.encrypt_heart_rate(hr_data)
    print(f"\n   Heart Rate: {len(hr_data)} samples encrypted")
    print(f"   Original mean: {np.mean(hr_data):.2f} BPM")
    print(f"   Encrypted mean: {encryptor.compute_encrypted_mean(encrypted_hr, len(hr_data)):.2f} BPM")

    # Batch encrypt bio-signals
    print("\n3. Batch Encrypting Bio-Signals...")
    bio_batch = encryptor.encrypt_biosignal_batch(
        spo2=spo2_data,
        heart_rate=hr_data
    )
    print(f"   Encrypted signals: {list(bio_batch.keys())}")

    # Test motion sensor encryption
    print("\n4. Encrypting Motion Sensor Data...")

    # Generate and encrypt accelerometer
    accel_x, accel_y, accel_z = generate_mock_accelerometer(10, 100)
    encrypted_accel = encryptor.encrypt_accelerometer(accel_x, accel_y, accel_z)
    print(f"   Accelerometer: 3 axes encrypted ({len(accel_x)} samples each)")
    print(f"   Z-axis mean (gravity): {np.mean(accel_z):.2f} m/s²")

    # Generate and encrypt GPS
    gps_lat, gps_lon = generate_mock_gps(100)
    encrypted_gps = encryptor.encrypt_gps_coordinates(gps_lat, gps_lon)
    print(f"\n   GPS: {len(gps_lat)} coordinate pairs encrypted")
    print(f"   Start: ({gps_lat[0]:.4f}, {gps_lon[0]:.4f})")
    print(f"   End: ({gps_lat[-1]:.4f}, {gps_lon[-1]:.4f})")

    # Test encrypted operations
    print("\n5. Testing Encrypted Operations...")

    # Create two simple vectors
    data1 = [1.0, 2.0, 3.0, 4.0, 5.0]
    data2 = [2.0, 3.0, 4.0, 5.0, 6.0]

    enc1 = encryptor.encrypt_data(data1)
    enc2 = encryptor.encrypt_data(data2)

    # Addition
    enc_sum = encryptor.add_encrypted(enc1, enc2)
    dec_sum = encryptor.decrypt_data(enc_sum)
    print(f"   {data1} + {data2}")
    print(f"   = {[f'{x:.2f}' for x in dec_sum[:5]]}")

    # Scaling
    enc_scaled = encryptor.scale_encrypted(enc1, 2.0)
    dec_scaled = encryptor.decrypt_data(enc_scaled)
    print(f"\n   {data1} * 2.0")
    print(f"   = {[f'{x:.2f}' for x in dec_scaled[:5]]}")

    # Verify encryption accuracy
    print("\n6. Verifying Encryption Accuracy...")
    is_valid = encryptor.verify_encryption(spo2_data, encrypted_spo2)
    print(f"   SpO2 encryption valid: {is_valid}")

    print("\n" + "="*60)
    print("IOT Data Encryption Demo Completed!")
    print("="*60)

    # Return encrypted data for external testing
    return {
        'bio_signals': bio_batch,
        'motion': encrypted_accel,
        'gps': encrypted_gps,
        'encryptor': encryptor
    }


if __name__ == "__main__":
    # Run demo and get encrypted data for testing
    encrypted_iot_data = demo_iot_encryption()

    print("\nEncrypted data is now available for testing!")
    print(f"Available datasets: {list(encrypted_iot_data.keys())}")
