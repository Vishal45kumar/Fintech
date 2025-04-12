import mongoose, { Schema } from "mongoose";

const billSchema = new mongoose.Schema({
  name: String,
  email: String,
  dueDate: Date,
  amount: Number,
});

export default mongoose.model("Bill", billSchema);
