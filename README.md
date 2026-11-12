# Manicure Booking Telegram Bot 💅

A feature-rich Telegram bot designed to automate appointment booking and schedule management for manicure services.

### Features

- **Appointment Booking:** Interactive calendar with available dates and time slots.
- **Automated Scheduling:** Monthly availability management with automatic slot reservation.
- **Customer Management:** Collects customer names and phone numbers.
- **Booking Cancellation:** Allows customers to cancel appointments and makes cancelled slots available again.
- **Admin Panel:** Manage working days, time slots, appointments, and daily schedules.
- **Appointment Notifications:** Automatically sends booking details to the administrator and updates a dedicated Telegram channel.
- **Automated Reminders:** Sends appointment reminders 24 hours before scheduled visits.
- **Service Pricing:** Displays available services and their prices.
- **Portfolio:** Provides direct access to the service portfolio.
- **Channel Subscription Verification:** Requires users to subscribe to a specified Telegram channel before booking.

### Tech Stack

- Python
- aiogram
- SQLite
- APScheduler
- FSM (Finite State Machine)
- Telegram Bot API
- HTML message formatting

### Key Highlights

- Structured, modular project architecture.
- Database-backed appointment management.
- Prevention of duplicate bookings and multiple active appointments per customer.
- Automatic restoration of scheduled reminders after bot restarts.
- Role-based administrator access.
- Interactive inline keyboard interface.

**Purpose:** To simplify appointment management, reduce manual communication, and provide a convenient booking experience for both customers and service providers.
