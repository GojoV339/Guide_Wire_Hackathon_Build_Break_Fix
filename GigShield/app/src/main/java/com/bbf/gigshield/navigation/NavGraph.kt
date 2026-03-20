package com.bbf.gigshield.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.bbf.gigshield.screens.BuyPolicyScreen
import com.bbf.gigshield.screens.LiveCoverageScreen
import com.bbf.gigshield.screens.OnboardingScreen
import com.bbf.gigshield.screens.PayoutScreen
import com.bbf.gigshield.screens.SplashScreen

@Composable
fun NavGraph(navController: NavHostController) {
    NavHost(
        navController = navController,
        startDestination = "splash"
    ) {
        composable("splash") {
            SplashScreen(navController = navController)
        }
        composable("onboarding") {
            OnboardingScreen(navController = navController)
        }
        composable("buy_policy") {
            BuyPolicyScreen(navController = navController)
        }
        composable("live_coverage") {
            LiveCoverageScreen(navController = navController)
        }
        composable("payout") {
            PayoutScreen(navController = navController)
        }
    }
}
