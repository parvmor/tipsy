package tipsy.db.schema

import tipsy.db.Constraints._

import slick.driver.PostgresDriver.api._

case class Program (
  id: Int,
  userId: String,
  time: String,
  quesId: String,
  code: String,
  score: String
)

class Programs(tag: Tag) extends
    Table[Program](tag, "PROGRAMS") with WithPrimaryKey {

  def id: Rep[Int] = column[Int]("SUB_ID", O.PrimaryKey, O.AutoInc)
  def userId: Rep[String] = column[String]("USER_ID")
  def time: Rep[String] = column[String]("SUB_TIME")
  def quesId: Rep[String] = column[String]("QUES_ID")
  def code: Rep[String] = column[String]("CODE")
  def score: Rep[String] = column[String]("SCORE")


  def * = (
    (id, userId, time, quesId, code, score) <>
      ((Program.apply _).tupled, Program.unapply)
  )
}