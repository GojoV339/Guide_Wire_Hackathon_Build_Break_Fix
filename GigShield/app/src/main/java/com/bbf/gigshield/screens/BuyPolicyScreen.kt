package com.bbf.gigshield.screens

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
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
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import com.bbf.gigshield.ui.theme.GigShieldAmber
import com.bbf.gigshield.ui.theme.GigShieldAmberPale
import com.bbf.gigshield.ui.theme.GigShieldGray
import com.bbf.gigshield.ui.theme.GigShieldGreen
import com.bbf.gigshield.ui.theme.GigShieldGreenLight
import androidx.compose.foundation.shape.RoundedCornerShape

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BuyPolicyScreen(navController: NavHostController) {

    val basePremium = 29.0
    val dailyEarnings = 700.0
    val weeklyEarnings = dailyEarnings * 7
    val earningsLinked = weeklyEarnings * 0.014
    val riskScore = 4.2
    val zoneRiskLoading = riskScore * 1.5
    val claimsSurcharge = 0.0
    val totalPremium = remember {
        basePremium + earningsLinked + zoneRiskLoading + claimsSurcharge
    }
    val maxCoverage = remember { weeklyEarnings * 0.85 }

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
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {

            // Worker profile card
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(4.dp),
                shape = RoundedCornerShape(12.dp)
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.Person,
                        contentDescription = null,
                        tint = GigShieldGreen,
                        modifier = Modifier.size(40.dp)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text("Ravi Kumar", fontWeight = FontWeight.Bold, fontSize = 16.sp)
                        Text("Koramangala, Bengaluru 560034", fontSize = 13.sp, color = GigShieldGray)
                        Text("Zepto Delivery Partner", fontSize = 13.sp, color = GigShieldGray)
                        Text("Daily earnings: ₹700", fontSize = 13.sp, color = GigShieldGray)
                    }
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Risk score card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = GigShieldAmberPale),
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Your Risk Score", fontSize = 13.sp, color = GigShieldGray)
                    Text(
                        "4.2 / 10",
                        fontSize = 28.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFFE65100)
                    )
                    Text(
                        "Based on your zone's 90-day disruption history",
                        fontSize = 12.sp,
                        color = GigShieldGray
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Premium breakdown card
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(4.dp),
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Premium Breakdown", fontWeight = FontWeight.Bold, fontSize = 15.sp)
                    Spacer(modifier = Modifier.height(8.dp))
                    PremiumRow("Base premium", "₹29.00")
                    PremiumRow("Earnings-linked (1.4%)", "₹${"%.2f".format(earningsLinked)}")
                    PremiumRow("Zone risk loading", "₹${"%.2f".format(zoneRiskLoading)}")
                    PremiumRow("Claims surcharge", "₹0.00")
                    HorizontalDivider(modifier = Modifier.padding(vertical = 8.dp))
                    PremiumRow(
                        "Total weekly premium",
                        "₹${"%.2f".format(totalPremium)}",
                        bold = true,
                        valueColor = GigShieldGreenLight
                    )
                    PremiumRow("Max coverage", "₹${"%.2f".format(maxCoverage)}")
                }
            }

            Spacer(modifier = Modifier.height(8.dp))
            Text(
                "Coverage: Mon 24 Mar — Sun 30 Mar 2026",
                fontSize = 13.sp,
                color = GigShieldGray,
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(12.dp))

            // What is covered card
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(2.dp),
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("What is covered", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    Spacer(modifier = Modifier.height(8.dp))
                    listOf(
                        "Heavy rainfall > 25mm/hr",
                        "Severe AQI > 300",
                        "Extreme heat > 42°C",
                        "Zone curfew or strike",
                        "Platform app outage > 2 hours"
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
                Text(
                    "Activate Policy — ₹${"%.2f".format(totalPremium)}",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(8.dp))
            Text(
                "Auto-renews every Monday. Cancel anytime.",
                fontSize = 12.sp,
                color = GigShieldGray,
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(16.dp))
        }
    }
}

@Composable
fun PremiumRow(
    label: String,
    value: String,
    bold: Boolean = false,
    valueColor: Color = Color.Unspecified
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 2.dp)
    ) {
        Text(
            label,
            fontSize = 13.sp,
            fontWeight = if (bold) FontWeight.Bold else FontWeight.Normal,
            modifier = Modifier.weight(1f)
        )
        Text(
            value,
            fontSize = 13.sp,
            fontWeight = if (bold) FontWeight.Bold else FontWeight.Normal,
            color = if (valueColor != Color.Unspecified) valueColor else Color.Unspecified
        )
    }
}

