package com.bbf.gigshield.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val LightColorScheme = lightColorScheme(
    primary = GigShieldGreen,
    onPrimary = GigShieldBackground,
    secondary = GigShieldAmber,
    onSecondary = GigShieldBackground,
    background = GigShieldBackground,
    surface = GigShieldSurface,
    onBackground = androidx.compose.ui.graphics.Color(0xFF1C1B1F),
    onSurface = androidx.compose.ui.graphics.Color(0xFF1C1B1F)
)

@Composable
fun GigShieldTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = LightColorScheme,
        typography = GigShieldTypography,
        content = content
    )
}
