import connectDB from "./db/mongo.js";
import express from 'express'
import cron from 'node-cron'
import nodemailer from 'nodemailer'
import Bill from "./models/Bill.js"
import cors from 'cors'
import dotenv from "dotenv";
dotenv.config({
  path: ".env",
});
const app = express();
app.use(express.json());
app.use(
  cors({
    origin: process.env.CORS_ORIGIN,
    credentials: true,
  })
);

const PORT = process.env.PORT || 8000
connectDB()
  .then(
    app.listen(PORT, () => {
      console.log(`Server is running on port ${PORT}`);
    })
  )
  .catch((error) => {
    console.log(`MOngodb connection error`, error);
  });

app.post("/add-bill", async (req, res) => {
  
  try {
    const { name, email, dueDate, amount } = req.body;

    // Validate inputs (optional)
    if (!name || !email || !dueDate || !amount) {
      return res.status(400).send("Missing fields");
    }

    const newBill = new Bill({ name, email, dueDate, amount });
    await newBill.save();
     const testMail = await transporter.sendMail({
       from: "vishalkumarchoubey1234@gmail.com",
       to: email,
       subject: "Test Email: Bill Added Successfully",
       text: `Hi ${name}, your bill of ₹${amount} has been added and is due on ${new Date(
         dueDate
       ).toDateString()}.`,
     });


    console.log("✅ New bill saved:", newBill);
    res.status(201).send("Bill added successfully");
  } catch (err) {
    console.error("❌ Error saving bill:", err);
    res.status(500).send("Server error while saving bill");
  }
});

// Email transporter
const transporter = nodemailer.createTransport({
  service: "gmail",
  auth: {
    user: "vishalkumarchoubey1234@gmail.com", // replace with your email
    pass: "tynixrxcqgboessv", // generate app password from Google
  },
});

// Cron job runs every day at 9 AM
cron.schedule("* * * * *", async () => {
  console.log("Checking bills every minute...");
  const today = new Date();
  const reminderDay = new Date(today);
  reminderDay.setDate(today.getDate() + 1); // Reminder one day before due

  const bills = await Bill.find({
    dueDate: {
      $lte: reminderDay,
      $gte: today,
    },
  });

  bills.forEach((bill) => {
    const mailOptions = {
      from: "vishalkumarchoubey1234@gmail.com",
      to: bill.email,
      subject: "Bill Payment Reminder",
      text: `Hi ${bill.name},\n\nThis is a reminder that your bill of amount ₹${
        bill.amount
      } is due on ${bill.dueDate.toDateString()}.\n\nPlease make the payment on time.`,
    };

    transporter.sendMail(mailOptions, (error, info) => {
      if (error) console.log("Email failed", error);
      else console.log("Email sent: " + info.response);
    });
  });
});

// app.listen(PORT, () => {
//   console.log("Server started on http://localhost:3000");
// });
