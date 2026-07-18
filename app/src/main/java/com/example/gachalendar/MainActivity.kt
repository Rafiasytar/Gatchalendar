package com.example.gachalendar

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
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
import com.example.gachalendar.ui.theme.GachalendarTheme
import com.example.gachalendar.viewmodel.GachaViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
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

    NavHost(navController = navController, startDestination = "dashboard") {
        composable("dashboard") {
            DashboardScreen(
                games = games,
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
                }
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
                    }
                )
            }
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