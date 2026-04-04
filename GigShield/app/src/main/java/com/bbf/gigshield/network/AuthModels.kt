package com.bbf.gigshield.network

import com.google.gson.annotations.SerializedName

data class OtpRequestDto(
    @SerializedName("phone_number") val phoneNumber: String,
)

data class OtpVerifyDto(
    @SerializedName("phone_number") val phoneNumber: String,
    val otp: String,
)

data class SendOtpResponseDto(
    val message: String,
    val phone: String,
    val otp: String? = null,
    @SerializedName("dev_note") val devNote: String? = null,
)

data class TokenResponseDto(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("token_type") val tokenType: String,
    @SerializedName("worker_id") val workerId: String,
)

data class WorkerProfileUpdateDto(
    val name: String?,
    @SerializedName("home_zone_pincode") val homeZonePincode: String?,
    @SerializedName("daily_earnings_declared") val dailyEarningsDeclared: Double?,
    @SerializedName("upi_id") val upiId: String?,
    @SerializedName("platform_partner_id") val platformPartnerId: String?
)
