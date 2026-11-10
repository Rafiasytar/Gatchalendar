package com.example.gachalendar

import android.os.Bundle
import android.os.Build
import com.example.gachalendar.notification.EventNotificationManager
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.example.gachalendar.ui.CombinedCalendarScreen
import com.example.gachalendar.ui.DashboardScreen
import com.example.gachalendar.ui.EventDetailScreen
import com.example.gachalendar.ui.GameCalendarScreen
import com.example.gachalendar.ui.HistoryScreen
import com.example.gachalendar.ui.SplashScreen
import com.example.gachalendar.ui.theme.GachalendarTheme
import com.example.gachalendar.viewmodel.GachaViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        // Initialize notification channel
        EventNotificationManager.createNotificationChannel(this)

        // Request POST_NOTIFICATIONS permission for Android 13+
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS) != android.content.pm.PackageManager.PERMISSION_GRANTED) {
                requestPermissions(arrayOf(android.Manifest.permission.POST_NOTIFICATIONS), 101)
            }
        }

        setContent {
            GachalendarTheme {
                GachalendarApp()
            }
        }
    }
}

@Composable
fun GachalendarApp() {
    val navController = rememberNavController()
    val viewModel: GachaViewModel = viewModel()
    
    val games by viewModel.games.collectAsState()
    val events by viewModel.events.collectAsState()

    // Ambil jadwal terbaru setiap kali aplikasi dibuka / kembali ke foreground
    val lifecycleOwner = LocalLifecycleOwner.current
    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_START) viewModel.refreshIfStale()
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }

    NavHost(navController = navController, startDestination = "splash") {
        composable("splash") {
            SplashScreen(
                onAnimationFinished = {
                    navController.navigate("dashboard") {
                        popUpTo("splash") { inclusive = true }
                    }
                }
            )
        }

        composable("dashboard") {
            val isLoading by viewModel.isLoading.collectAsState()
            DashboardScreen(
                games = games,
                events = events,
                isRefreshing = isLoading,
                onRefresh = { viewModel.refreshEvents() },
                onGameClick = { gameId ->
                    navController.navigate("game_calendar/$gameId")
                },
                onCombinedCalendarClick = {
                    navController.navigate("combined_calendar")
                }
            )
        }
        
        composable("combined_calendar") {
            CombinedCalendarScreen(
                events = events,
                onBackClick = { navController.popBackStack() },
                onEventClick = { event ->
                    navController.navigate("eventDetail/${event.id}")
                },
                onRefresh = { viewModel.refreshEvents() },
                onHistoryClick = { navController.navigate("history?gameId=") }
            )
        }
        
        composable(
            "game_calendar/{gameId}",
            arguments = listOf(navArgument("gameId") { type = NavType.StringType })
        ) { backStackEntry ->
            val gameId = backStackEntry.arguments?.getString("gameId")
            val game = games.find { it.id == gameId }
            
            if (game != null) {
                GameCalendarScreen(
                    game = game,
                    events = events,
                    onBackClick = { navController.popBackStack() },
                    onEventClick = { event ->
                        navController.navigate("eventDetail/${event.id}")
                    },
                    onRefresh = { viewModel.refreshEvents() },
                    onHistoryClick = { navController.navigate("history?gameId=$gameId") }
                )
            }
        }

        composable(
            "history?gameId={gameId}",
            arguments = listOf(
                navArgument("gameId") {
                    type = NavType.StringType
                    nullable = true
                    defaultValue = null
                }
            )
        ) { backStackEntry ->
            val gameId = backStackEntry.arguments?.getString("gameId")
            val realGameId = if (gameId.isNullOrEmpty()) null else gameId
            HistoryScreen(
                events = events,
                gameId = realGameId,
                onBackClick = { navController.popBackStack() },
                onEventClick = { event ->
                    navController.navigate("eventDetail/${event.id}")
                }
            )
        }

        composable(
            "eventDetail/{eventId}",
            arguments = listOf(navArgument("eventId") { type = NavType.StringType })
        ) { backStackEntry ->
            val eventId = backStackEntry.arguments?.getString("eventId")
            val event = events.find { it.id == eventId }
            if (event != null) {
                EventDetailScreen(
                    event = event,
                    onBackClick = { navController.popBackStack() }
                )
            }
        }
    }
}