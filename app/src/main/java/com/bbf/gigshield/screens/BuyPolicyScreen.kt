package com.bbf.gigshield.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.wrapContentWidth
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CenterAlignedTopAppBar
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import com.bbf.gigshield.ui.theme.GigShieldAmber
import com.bbf.gigshield.ui.theme.GigShieldAmberPale
import com.bbf.gigshield.ui.theme.GigShieldBlueInfo
import com.bbf.gigshield.ui.theme.GigShieldGray
import com.bbf.gigshield.ui.theme.GigShieldGreen
import com.bbf.gigshield.ui.theme.GigShieldGreenLight

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BuyPolicyScreen(navController: NavHostController) {
    val basePremium = 29.0
    val dailyEarnings = 700.0
    val weeklyEarnings = dailyEarnings * 7
    val earningsLinked = weeklyEarnings * 0.014
    val riskScore = 4.2
    val zoneRiskLoading = riskScore * 1.5
    val totalPremium = basePremium + earningsLinked + zoneRiskLoading

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Buy Policy", fontWeight = FontWeight.Bold) },
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                    containerColor = GigShieldGreen,
                    titleContentColor = Color.White
                )
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .padding(paddingValues)
                .padding(horizontal = 16.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(modifier = Modifier.height(16.dp))

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.Person,
                        contentDescription = null,
                        tint = GigShieldGreen,
                        modifier = Modifier.size(42.dp)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text("Ravi Kumar", fontWeight = FontWeight.Bold, fontSize = 16.sp)
                        Text(
                            "Koramangala, Bengaluru 560034",
                            fontSize = 13.sp,
                            color = GigShieldGray
                        )
                        Text(
                            "Zepto Delivery Partner",
                            fontSize = 13.sp,
                            color = GigShieldGray
                        )
                        Text(
                            "Daily earnings: ₹700",
                            fontSize = 13.sp,
                            color = GigShieldGray
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                elevation = CardDefaults.cardElevation(defaultElevation = 0.dp),
                colors = CardDefaults.cardColors(containerColor = GigShieldAmberPale)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Your Risk Score", fontSize = 13.sp, color = GigShieldGray)
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        "4.2 / 10",
                        fontSize = 28.sp,
                        fontWeight = FontWeight.Bold,
                        color = GigShieldAmber
                    )
                    Text(
                        "Based on zone's history",
                        fontSize = 12.sp,
                        color = GigShieldGray
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        "Premium Breakdown",
                        fontWeight = FontWeight.Bold,
                        fontSize = 15.sp
                    )
                    Spacer(modifier = Modifier.height(10.dp))

                    PremiumRow(
                        label = "Base premium",
                        value = "₹${"%.2f".format(basePremium)}"
                    )
                    PremiumRow(
                        label = "Earnings-linked (1.4%)",
                        value = "₹${"%.2f".format(earningsLinked)}"
                    )
                    PremiumRow(
                        label = "Zone risk loading",
                        value = "₹${"%.2f".format(zoneRiskLoading)}"
                    )

                    HorizontalDivider(modifier = Modifier.padding(vertical = 8.dp))

                    PremiumRow(
                        label = "Total weekly premium",
                        value = "₹${"%.2f".format(totalPremium)}",
                        bold = true,
                        valueColor = GigShieldGreenLight
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("What is covered", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    Spacer(modifier = Modifier.height(8.dp))

                    listOf(
                        "Heavy rainfall over 25mm",
                        "Severe AQI over 300",
                        "Extreme heat over 42 degrees",
                        "Zone curfew or strike",
                        "Platform app outage over 2 hours"
                    ).forEach { item ->
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.padding(vertical = 3.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.CheckCircle,
                                contentDescription = null,
                                tint = GigShieldGreen,
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(item, fontSize = 13.sp)
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = { navController.navigate("live_coverage") },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                colors = ButtonDefaults.buttonColors(containerColor = GigShieldGreen),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text("Activate Policy", fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }

            Spacer(modifier = Modifier.height(16.dp))
        }
    }
}

@Composable
private fun PremiumRow(
    label: String,
    value: String,
    bold: Boolean = false,
    valueColor: Color = Color.Unspecified
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            label,
            fontSize = 13.sp,
            fontWeight = if (bold) FontWeight.Bold else FontWeight.Normal,
            color = GigShieldGray
        )
        Text(
            value,
            fontSize = 13.sp,
            fontWeight = if (bold) FontWeight.Bold else FontWeight.Normal,
            color = if (valueColor != Color.Unspecified) valueColor else Color.Unspecified
        )
    }
}

