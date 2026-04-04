package com.bbf.gigshield.screens

import android.widget.Toast
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.bbf.gigshield.network.ApiClient
import com.bbf.gigshield.network.OtpRequestDto
import com.bbf.gigshield.network.OtpVerifyDto
import com.bbf.gigshield.data.TokenStore
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OnboardingScreen(navController: NavController) {
    var step by remember { mutableStateOf(1) }
    var phone by remember { mutableStateOf("") }
    var platform by remember { mutableStateOf("Zepto") }
    var platformId by remember { mutableStateOf("") }
    var otp by remember { mutableStateOf("") }
    var showError by remember { mutableStateOf(false) }
    var loading by remember { mutableStateOf(false) }
    var devOtpHint by remember { mutableStateOf<String?>(null) }
    var expanded by remember { mutableStateOf(false) }
    
    val platforms = listOf("Zepto", "Blinkit", "Instamart", "Swiggy", "Zomato")
    val scope = rememberCoroutineScope()
    val context = LocalContext.current

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        if (step == 1) {
            Text(
                text = "GigShield",
                color = Color(0xFF1B5E20),
                fontSize = 36.sp,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = "Income protection for delivery workers",
                color = Color.Gray,
                fontSize = 14.sp
            )
            Spacer(modifier = Modifier.height(40.dp))

            // Platform Selection
            ExposedDropdownMenuBox(
                expanded = expanded,
                onExpandedChange = { expanded = !expanded },
                modifier = Modifier.fillMaxWidth()
            ) {
                OutlinedTextField(
                    value = platform,
                    onValueChange = {},
                    readOnly = true,
                    label = { Text("Delivery Platform") },
                    trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
                    modifier = Modifier.menuAnchor().fillMaxWidth()
                )
                ExposedDropdownMenu(
                    expanded = expanded,
                    onDismissRequest = { expanded = false }
                ) {
                    platforms.forEach { selectionOption ->
                        DropdownMenuItem(
                            text = { Text(selectionOption) },
                            onClick = {
                                platform = selectionOption
                                expanded = false
                            }
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            OutlinedTextField(
                value = platformId,
                onValueChange = { platformId = it },
                label = { Text("$platform Partner ID") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )

            Spacer(modifier = Modifier.height(16.dp))

            OutlinedTextField(
                value = phone,
                onValueChange = { phone = it },
                label = { Text("Mobile Number") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            Button(
                onClick = {
                    if (phone.length < 10) {
                        Toast.makeText(context, "Enter valid phone number", Toast.LENGTH_SHORT).show()
                        return@Button
                    }
                    scope.launch {
                        loading = true
                        try {
                            val response = ApiClient.getAuthApi(context).sendOtp(OtpRequestDto(phone))
                            if (response.isSuccessful) {
                                devOtpHint = "Dev OTP: ${response.body()?.otp}"
                                step = 2
                                Toast.makeText(context, "OTP Sent", Toast.LENGTH_SHORT).show()
                            } else {
                                val errorBody = response.errorBody()?.string()
                                Toast.makeText(context, "Error: $errorBody", Toast.LENGTH_LONG).show()
                                showError = true
                            }
                        } catch (e: Exception) {
                            Toast.makeText(context, "Connection Error: ${e.message}", Toast.LENGTH_LONG).show()
                            showError = true
                        } finally {
                            loading = false
                        }
                    }
                },
                modifier = Modifier.fillMaxWidth().height(50.dp),
                enabled = !loading,
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1B5E20))
            ) {
                if (loading) CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
                else Text("Send OTP")
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "By continuing you agree to our Terms and Privacy Policy",
                color = Color.Gray,
                fontSize = 12.sp,
                textAlign = TextAlign.Center
            )
        } else {
            Text(
                text = "OTP sent to +91 $phone",
                textAlign = TextAlign.Center,
                fontSize = 16.sp
            )
            devOtpHint?.let {
                Text(text = it, color = Color.Gray, fontSize = 12.sp)
            }
            Spacer(modifier = Modifier.height(24.dp))
            OutlinedTextField(
                value = otp,
                onValueChange = { 
                    otp = it
                    showError = false 
                },
                label = { Text("Enter OTP") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(8.dp))
            if (showError) {
                Text(
                    text = "Incorrect OTP. Please try again.",
                    color = Color.Red,
                    fontSize = 12.sp
                )
            }
            Spacer(modifier = Modifier.height(16.dp))
            Button(
                onClick = {
                    scope.launch {
                        loading = true
                        try {
                            val response = ApiClient.getAuthApi(context).verifyOtp(OtpVerifyDto(phone, otp))
                            if (response.isSuccessful && response.body() != null) {
                                TokenStore.saveAccessToken(context, response.body()!!.accessToken)
                                navController.navigate("complete_profile") {
                                    popUpTo("onboarding") { inclusive = true }
                                }
                            } else {
                                Toast.makeText(context, "Invalid OTP", Toast.LENGTH_SHORT).show()
                                showError = true
                            }
                        } catch (e: Exception) {
                            Toast.makeText(context, "Verify Error: ${e.message}", Toast.LENGTH_LONG).show()
                            showError = true
                        } finally {
                            loading = false
                        }
                    }
                },
                modifier = Modifier.fillMaxWidth().height(50.dp),
                enabled = !loading,
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1B5E20))
            ) {
                if (loading) CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
                else Text("Verify OTP")
            }
            Spacer(modifier = Modifier.height(8.dp))
            TextButton(onClick = { step = 1 }) {
                Text("Change Details", color = Color(0xFF1B5E20))
            }
        }
    }
}
