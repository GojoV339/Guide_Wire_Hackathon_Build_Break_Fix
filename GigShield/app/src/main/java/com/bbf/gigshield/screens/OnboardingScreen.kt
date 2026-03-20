package com.bbf.gigshield.screens

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import com.bbf.gigshield.ui.theme.GigShieldGreen
import com.bbf.gigshield.ui.theme.GigShieldGray

@Composable
fun OnboardingScreen(navController: NavHostController) {

    var step by remember { mutableStateOf(1) }
    var phone by remember { mutableStateOf("") }
    var otp by remember { mutableStateOf("") }
    var showError by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Spacer(modifier = Modifier.height(60.dp))

        Text(
            text = "GigShield",
            fontSize = 36.sp,
            fontWeight = FontWeight.Bold,
            color = GigShieldGreen
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = "Income protection for delivery workers",
            fontSize = 14.sp,
            color = GigShieldGray,
            textAlign = TextAlign.Center
        )
        Spacer(modifier = Modifier.height(48.dp))

        if (step == 1) {
            OutlinedTextField(
                value = phone,
                onValueChange = { if (it.length <= 10) phone = it },
                label = { Text("Mobile Number") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(16.dp))
            Button(
                onClick = { if (phone.length == 10) step = 2 },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                colors = ButtonDefaults.buttonColors(containerColor = GigShieldGreen)
            ) {
                Text("Send OTP", fontSize = 16.sp)
            }
            Spacer(modifier = Modifier.height(12.dp))
            Text(
                text = "By continuing you agree to our Terms and Privacy Policy",
                fontSize = 12.sp,
                color = GigShieldGray,
                textAlign = TextAlign.Center
            )
        } else {
            Text(
                text = "OTP sent to +91 $phone",
                fontSize = 14.sp,
                color = GigShieldGray,
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(24.dp))
            OutlinedTextField(
                value = otp,
                onValueChange = { if (it.length <= 4) otp = it },
                label = { Text("Enter OTP") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )
            if (showError) {
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Incorrect OTP. Please try 1234",
                    color = Color.Red,
                    fontSize = 12.sp
                )
            }
            Spacer(modifier = Modifier.height(16.dp))
            Button(
                onClick = {
                    if (otp == "1234") {
                        navController.navigate("buy_policy") {
                            popUpTo("onboarding") { inclusive = true }
                        }
                    } else {
                        showError = true
                    }
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                colors = ButtonDefaults.buttonColors(containerColor = GigShieldGreen)
            ) {
                Text("Verify OTP", fontSize = 16.sp)
            }
            Spacer(modifier = Modifier.height(8.dp))
            TextButton(onClick = { }) {
                Text("Resend OTP", color = GigShieldGreen)
            }
        }
    }
}

